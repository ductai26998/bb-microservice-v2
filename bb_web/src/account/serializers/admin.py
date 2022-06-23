from rest_framework import serializers

from .. import models


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BaseUser
        fields = [
            "id",
            "email",
            "username",
            "is_active",
            "is_salon",
            "is_superuser",
        ]
