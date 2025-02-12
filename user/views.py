from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializer import UserSerializer


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    # serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
