from django.urls import path, include
from rest_framework import routers

from air_service import views

router = routers.DefaultRouter()
router.register(r"cities", views.CityViewSet)
router.register(r"countries", views.CountryViewSet)
router.register(r"airports", views.AirportViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "air_service"
