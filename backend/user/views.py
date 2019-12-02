from rest_framework import generics, authentication, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer, \
                             ChangePasswordSerializer, \
                             PasswordRecoverySerializer
from user.utils import PasswordRecoveryMail


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """ Manage the authenticated user """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """ Retrieve and return authentication user """
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """ An endpoint for changing password."""
    serializer_class = ChangePasswordSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            old_pw = serializer.data.get("old_password")
            if not self.object.check_password(old_pw):
                return Response({"old_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            new_pw = serializer.data.get("new_password")
            new_pw2 = serializer.data.get("new_password2")
            if new_pw != new_pw2:
                return Response({"new_password": ["Passwords do not match."]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(new_pw)
            self.object.save()
            return Response("Success.", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryView(APIView):
    """ User recovers password. """
    def post(self, request, format=None):
        serializer = PasswordRecoverySerializer(
            data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            try:
                PasswordRecoveryMail(email=email).send()
            except Exception as e:
                err_msg = str(e)
                raise AssertionError(err_msg)
            else:
                return Response(serializer.data,
                                status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)