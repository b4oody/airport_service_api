from rest_framework import serializers

from air_service.models import Country, City, Airport


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
