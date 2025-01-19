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
        fields = ["id", "country_name", ]


class CitySerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(slug_field="country_name", read_only=True)

    class Meta:
        model = City
        fields = ["id", "city_name", "country"]


class AirportSerializer(serializers.ModelSerializer):
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


class AirplaneListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = [
            "id",
            "airplane_name",
            "rows",
            "seats_in_row",
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
    source = serializers.SlugRelatedField(
        read_only=True,
        slug_field="airport_name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field="airport_name"
    )

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class CrewRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "full_name"]


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    airplane = AirplaneListSerializer()
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

    class Meta:
        model = Flight
        fields = ["id", "route", "departure_datetime", "arrival_datetime"]


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightListSerializer()


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketRetrieveSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "order_created_at", "user", "tickets"]
