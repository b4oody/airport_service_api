from rest_framework import viewsets

from air_service.models import (
    Country,
    City,
    Airport,
    Airplane,
    Route,
    Crew,
    Flight,
    Order,
)
from air_service.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportSerializer,
    AirplaneSerializer,
    RouteSerializer,
    # CrewListSerializer,
    FlightSerializer,
    CrewRetrieveSerializer,
    OrderSerializer,
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


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return AirplaneRetrieveSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewRetrieveSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        request = self.request
        return Order.objects.filter(user=request.user)
