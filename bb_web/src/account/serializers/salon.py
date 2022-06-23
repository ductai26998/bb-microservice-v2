# from booking import models as booking_models
from rest_framework import serializers

from ...service.serializers import ServiceSalonSerializer
from .. import models
from ..email import send_otp_to_email
from .address import AddressSerializerInput
# from .user import UserBaseViewSerializer


class SalonSerializer(serializers.ModelSerializer):
    services = ServiceSalonSerializer(many=True, read_only=True)

    class Meta:
        model = models.Salon
        fields = [
            "id",
            "avatar",
            "background_image",
            "description",
            "address",
            "email",
            "is_active",
            "is_closed",
            "is_verified",
            "phone_number",
            "salon_name",
            "total_completed_booking",
            "vote_rate",
            "total_reviews",
            "username",
            "first_name",
            "last_name",
            "is_salon",
            "is_superuser",
            "services",
        ]
        depth = 1


class SalonBaseViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Salon
        fields = [
            "id",
            "address",
            "phone_number",
            "salon_name",
            "username",
            "first_name",
            "last_name",
        ]
        depth = 1


class SalonRegisterInputSerializer(serializers.ModelSerializer):
    address = AddressSerializerInput()

    class Meta:
        model = models.Salon
        fields = [
            "email",
            "salon_name",
            "phone_number",
            "username",
            "first_name",
            "last_name",
            "password",
            "address",
        ]

    def create(self, validated_data):
        address_data = validated_data.pop("address")
        province = address_data.get("province") or ""
        district = address_data.get("district") or ""
        ward = address_data.get("ward") or ""
        hamlet = address_data.get("hamlet") or ""
        address_specific = hamlet + ", " + ward + ", " + district + ", " + province
        address_data["address"] = address_specific
        address = models.Address.objects.create(**address_data)
        salon = models.Salon.objects.create(**validated_data, address=address)
        return salon

    def save(self, **kwargs):
        super().save(**kwargs)

        password = self.validated_data["password"]
        instance = self.instance
        instance.set_password(password)
        instance.save()
        email = self.validated_data["email"]
        send_otp_to_email(instance, email)


class SalonRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Salon
        fields = [
            "id",
            "avatar",
            "email",
            "salon_name",
            "phone_number",
            "username",
            "is_verified",
            "address",
            "first_name",
            "last_name",
            "is_salon",
            "is_superuser",
        ]
        depth = 2


# class SalonReviewSerializer(serializers.ModelSerializer):
#     user = UserBaseViewSerializer(read_only=True)

#     class Meta:
#         model = booking_models.Booking
#         fields = [
#             "rating",
#             "review",
#             "user",
#         ]
