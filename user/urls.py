from django.urls import path

from user.views import UserCreateView, LoginUserView, ManageUserView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="create"),
    path("login/", LoginUserView.as_view(), name="get_token"),
    path("profile/", ManageUserView.as_view(), name="manage_user"),
]

app_name = "user"
