from rest_framework import viewsets

from air_service.models import (
    Country,
    City,
    Airport,
)
from air_service.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
