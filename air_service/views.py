from django.db.models import Prefetch, Count, F, Min, Max
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, filters

from air_service.models import (
    Country,
    City,
    Airport,
    Airplane,
    AirplaneType,
    Route,
    Crew,
    Flight,
    Order,
    Ticket,
)
from air_service.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportRetrieveSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    RouteSerializer,
    RouteListRetrieveSerializer,
    FlightSerializer,
    FlightListSerializer,
    CrewRetrieveSerializer,
    OrderSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    FlightRetrieveSerializer,
    OrderListRetrieveSerializer
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["country_name"]


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["city_name", "country__country_name"]

    def get_queryset(self):
        queryset = self.queryset
        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(
                country__country_name__icontains=country
            )
        if self.action == "list":
            return queryset.select_related("country")
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "country",
                type={"type": "string"},
                description="Filter by country name"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportRetrieveSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["airport_name", "city__city_name"]

    def get_queryset(self):
        queryset = self.queryset
        city = self.request.query_params.get("city")
        country = self.request.query_params.get("country")
        if city:
            queryset = queryset.filter(
                city__city_name__icontains=city
            )
        if country:
            queryset = queryset.filter(
                city__country__country_name__icontains=country
            )
        if self.action == "list":
            return queryset.select_related("city__country")
        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "city",
                type={"type": "string"},
                description="Filter by city name"
            ),
            OpenApiParameter(
                "country",
                type={"type": "string"},
                description="Filter by country name"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["type_name"]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["airplane_name", "airplane_type__type_name"]

    def get_queryset(self):
        queryset = self.queryset
        airplane_name = self.request.query_params.get("airplane_name")
        airplane_type = self.request.query_params.get("airplane_type")
        if airplane_name:
            queryset = queryset.filter(
                airplane_name__icontains=airplane_name
            )
        if airplane_type:
            queryset = queryset.filter(
                airplane_type__type_name__icontains=airplane_type
            )
        if self.action == "list":
            return queryset.select_related("airplane_type")

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "airplane name",
                type={"type": "string"},
                description="Filter by airplane name"
            ),
            OpenApiParameter(
                "airplane type",
                type={"type": "string"},
                description="Filter by airplane type"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "source__airport_name",
        "destination__airport_name",
    ]

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        if not hasattr(self, "_min_max"):
            self._min_max = queryset.aggregate(
                min=Min("distance"),
                max=Max("distance")
            )
        min_max = self._min_max

        distance_min = self.request.query_params.get(
            "distance_min",
            min_max["min"]
        )
        distance_max = self.request.query_params.get(
            "distance_max",
            min_max["max"]
        )
        if source:
            queryset = queryset.filter(
                source__airport_name__icontains=source
            )
        if destination:
            queryset = queryset.filter(
                destination__airport_name__icontains=destination
            )
        if distance_min or distance_max:
            queryset = queryset.filter(
                distance__gte=distance_min,
                distance__lte=distance_max
            )
        if self.action in ("list", "retrieve"):
            return queryset.select_related(
                "source__city__country",
                "destination__city__country",
            )
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListRetrieveSerializer
        return RouteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "min distance",
                type={"type": "integer"},
                description="Filter by min distance",
                default=0
            ),
            OpenApiParameter(
                "max distance",
                type={"type": "integer"},
                description="Filter by max distance",
                default=10000
            ),
            OpenApiParameter(
                "source",
                type={"type": "string"},
                description="Filter by by airport source"
            ),
            OpenApiParameter(
                "destination",
                type={"type": "string"},
                description="Filter by airport destination"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewRetrieveSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        queryset = self.queryset
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        if first_name:
            queryset = queryset.filter(
                first_name__icontains=first_name
            )
        if last_name:
            queryset = queryset.filter(
                last_name__icontains=last_name
            )
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first name",
                type={"type": "string"},
                description="Filter by first name",
            ),
            OpenApiParameter(
                "last name",
                type={"type": "string"},
                description="Filter by last name",
            ),

        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "route__source__airport_name",
        "route__destination__airport_name",
        "departure_datetime",
        "arrival_datetime",
    ]

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        departure_datetime = self.request.query_params.get(
            "departure_datetime"
        )
        arrival_datetime = self.request.query_params.get("arrival_datetime")
        if source:
            queryset = queryset.filter(
                route__source__airport_name__icontains=source
            )
        if destination:
            queryset = queryset.filter(
                route__destination__airport_name__icontains=destination
            )
        if departure_datetime:
            queryset = queryset.filter(
                departure_datetime__date=departure_datetime
            )
        if arrival_datetime:
            queryset = queryset.filter(
                arrival_datetime__date=arrival_datetime
            )

        if self.action in ("list", "retrieve"):
            return (queryset.select_related(
                "route__source",
                "route__destination",
                "airplane",
            ).prefetch_related("crew").annotate(
                tickets_available=F("airplane__rows")
                * F("airplane__seats_in_row")
                - Count("tickets")
            )
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "string"},
                description="Filter by by airport source"
            ),
            OpenApiParameter(
                "destination",
                type={"type": "string"},
                description="Filter by airport destination"
            ),
            OpenApiParameter(
                "departure_datetime",
                type={"type": "datetime"},
                description="Filter by departure datetime",
                default="2003-10-10"
            ),
            OpenApiParameter(
                "arrival_datetime",
                type={"type": "datetime"},
                description="Filter by arrival datetime",
                default="2023-10-10"
            ),

        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "order_created_at",
        "tickets__flight__route__source__airport_name",
        "tickets__flight__route__destination__airport_name"
    ]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        order_created_at = self.request.query_params.get("order_created_at")
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        if order_created_at:
            queryset = queryset.filter(
                order_created_at__date=order_created_at
            )
        if source:
            queryset = queryset.filter(
                tickets__flight__route__source__airport_name__icontains=source
            )
        if destination:
            queryset = queryset.filter(
                tickets__flight__route__destination__airport_name__icontains=destination
            )
        if self.action in ("list", "retrieve"):
            tickets_prefetch = Prefetch(
                "tickets",
                queryset=Ticket.objects.select_related(
                    "flight__route__source__city",
                    "flight__route__destination__city",
                ),
            )
            return queryset.prefetch_related(tickets_prefetch)
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderListRetrieveSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "string"},
                description="Filter by by airport source"
            ),
            OpenApiParameter(
                "destination",
                type={"type": "string"},
                description="Filter by airport destination"
            ),
            OpenApiParameter(
                "order_created_at",
                type={"type": "datetime"},
                description="Filter by created at",
                default="2003-10-10"
            ),


        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
