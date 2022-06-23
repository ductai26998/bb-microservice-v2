from rest_framework import serializers

from .address import AddressSerializer, AddressSerializerInput
from .admin import AdminSerializer
from .salon import (
    SalonRegisterInputSerializer,
    SalonRegisterSerializer,
    SalonSerializer,
)
# from .user import UserRegisterInputSerializer, UserRegisterSerializer, UserSerializer


class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
