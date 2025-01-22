from typing import Union

from django.db import transaction
from rest_framework import serializers

from air_service.models import (
    Country,
    City,
    Airport,
    Airplane,
    AirplaneType,
    Route,
    Crew,
    Flight,
    Ticket,
    Order,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "country_name"]


class CitySerializer(serializers.ModelSerializer):
    country = serializers.CharField()

    class Meta:
        model = City
        fields = ["id", "city_name", "country"]

    @transaction.atomic
    def create(self, validated_data):
        country_name = validated_data.pop("country")
        country, _ = Country.objects.get_or_create(country_name=country_name)
        city = City.objects.create(country=country, **validated_data)
        return city

    @transaction.atomic
    def update(self, instance, validated_data):
        country_name = validated_data.pop("country", None)
        if country_name:
            country, _ = Country.objects.get_or_create(
                country_name=country_name
            )
            instance.country = country
        instance.city_name = validated_data.get("city_name", instance.city_name)
        instance.save()
        return instance


class AirportRetrieveSerializer(serializers.ModelSerializer):
    city = serializers.SlugRelatedField(
        read_only=True,
        slug_field="city_name",
    )
    country = serializers.CharField(
        read_only=True,
        source="city.country.country_name",
    )

    class Meta:
        model = Airport
        fields = ["id", "airport_name", "city", "country"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "type_name"]


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField()

    class Meta:
        model = Airplane
        fields = ["id", "airplane_name", "rows", "seats_in_row", "airplane_type"]

    @transaction.atomic
    def create(self, validated_data):
        airplane_type = validated_data.pop("airplane_type")
        airplane_type, _ = AirplaneType.objects.get_or_create(
            type_name=airplane_type
        )
        airplane = Airplane.objects.create(airplane_type=airplane_type, **validated_data)
        return airplane

    @transaction.atomic
    def update(self, instance, validated_data):
        type_name = validated_data.pop("airplane_type", None)
        if type_name:
            airplane_type, _ = AirplaneType.objects.get_or_create(
                type_name=type_name
            )
            instance.airplane_type = airplane_type
        instance.airplane_name = validated_data.get("airplane_name", instance.airplane_name)
        instance.rows = validated_data.get("rows", instance.rows)
        instance.seats_in_row = validated_data.get("seats_in_row", instance.seats_in_row)
        instance.save()
        return instance


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        read_only=True,
        slug_field="type_name"
    )

    class Meta:
        model = Airplane
        fields = [
            "id",
            "airplane_name",
            "airplane_type",
            "total_seats",
        ]


class AirplaneRetrieveSerializer(AirplaneListSerializer):
    airplane_type = AirplaneTypeSerializer()

    class Meta:
        model = Airplane
        fields = [
            "id",
            "airplane_name",
            "rows",
            "seats_in_row",
            "airplane_type",
        ]


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.CharField()
    destination = serializers.CharField()

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]

    @staticmethod
    def get_airport_by_id_or_name(name_input: Union[str, int], field_name: str) -> Airport:
        if isinstance(name_input, int) or name_input.isdigit():
            try:
                airport = Airport.objects.get(id=int(name_input))
                return airport
            except Airport.DoesNotExist:
                raise serializers.ValidationError(
                    {field_name: f"Invalid {field_name} airport ID."}
                )
        else:
            airport = Airport.objects.filter(airport_name=name_input).first()
            if not airport:
                raise serializers.ValidationError(
                    {
                        field_name: f"{field_name.capitalize()} airport '{name_input}' "
                                    f"does not exist. Please create it first."}
                )
            print(f"Found airport for {field_name}: {airport}")
            return airport

    @transaction.atomic
    def create(self, validated_data):
        source_input = validated_data.pop("source")
        destination_input = validated_data.pop("destination")

        source_airport = self.get_airport_by_id_or_name(
            source_input, "source"
        )
        destination_airport = self.get_airport_by_id_or_name(
            destination_input, "destination"
        )

        if Route.objects.filter(
                source=source_airport,
                destination=destination_airport
        ).exists():
            raise serializers.ValidationError("This route already exists.")

        route = Route.objects.create(
            source=source_airport,
            destination=destination_airport,
            **validated_data
        )
        return route

    @transaction.atomic
    def update(self, instance, validated_data):
        source_input = validated_data.pop("source", None)
        destination_input = validated_data.pop("destination", None)

        if source_input:
            source_airport = self.get_airport_by_id_or_name(
                source_input, "source"
            )
            instance.source = source_airport
        if destination_input:
            destination_airport = self.get_airport_by_id_or_name(
                destination_input, "destination"
            )
            instance.destination = destination_airport

        instance.distance = validated_data.get("distance", instance.distance)
        instance.save()
        return instance


class RouteListRetrieveSerializer(RouteSerializer):
    source = AirportRetrieveSerializer()
    destination = AirportRetrieveSerializer()


class CrewRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "full_name"]


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.CharField(source="route.full_route")
    airplane = serializers.CharField(source="airplane.airplane_name")

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "crew",
            "departure_datetime",
            "arrival_datetime"
        ]


class FlightRetrieveSerializer(FlightSerializer):
    route = RouteSerializer()
    airplane = AirplaneRetrieveSerializer()
    crew = CrewRetrieveSerializer(many=True)


class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.CharField(source="route.full_route", read_only=True)
    airplane = serializers.SlugRelatedField(
        slug_field="airplane_name",
        read_only=True
    )

    # free_seats = serializers.IntegerField()

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "departure_datetime",
            "arrival_datetime",
            "airplane"
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "seat_row", "seat_number", "flight"]


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightListSerializer()


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketRetrieveSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "order_created_at", "user", "tickets"]
