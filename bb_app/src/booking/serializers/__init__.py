# from account.serializers.salon import SalonBaseViewSerializer
from rest_framework import serializers

from ...account.serializers.user import UserBaseViewSerializer
from ...core.serializers import MoneyField
from .. import models


class BookingServiceSerializer(serializers.ModelSerializer):
    price = MoneyField()

    class Meta:
        model = models.BookingService
        fields = [
            "id",
            "service",
            "price",
        ]
        depth = 1


class BookingSerializer(serializers.ModelSerializer):
    total_net = MoneyField()
    booking_services = BookingServiceSerializer(many=True, read_only=True)
    user = UserBaseViewSerializer(read_only=True)
    # salon = SalonBaseViewSerializer(read_only=True)

    class Meta:
        model = models.Booking
        fields = [
            "id",
            "created_at",
            "updated_at",
            "user",
            "salon",
            "status",
            "total_net",
            "booking_services",
            "rating",
            "review",
        ]
        depth = 1


class BookingCreateInputSerializer(serializers.Serializer):
    salon_id = serializers.CharField()
    service_ids = serializers.ListField(child=serializers.CharField())


class BookingReviewInputSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review = serializers.CharField(required=False, allow_blank=True)
