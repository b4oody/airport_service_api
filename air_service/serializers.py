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
    source = AirportRetrieveSerializer()
    destination = AirportRetrieveSerializer()

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class CrewRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "full_name"]


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    airplane = AirplaneRetrieveSerializer()
    crew = CrewRetrieveSerializer(many=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "crew",
            "departure_datetime",
            "arrival_datetime",
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "seat_row", "seat_number", "flight"]


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


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightListSerializer()


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketRetrieveSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "order_created_at", "user", "tickets"]
