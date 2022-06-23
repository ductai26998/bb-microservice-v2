from rest_framework import serializers

from .. import models


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = "__all__"


class AddressSerializerInput(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = [
            "hamlet",
            "ward",
            "district",
            "province",
            "position_url",
        ]
