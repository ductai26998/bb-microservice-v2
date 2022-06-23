from rest_framework import serializers

from ...core.serializers import MoneyField
from .. import models


class ServiceInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Service
        fields = [
            "name",
        ]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Service
        fields = [
            "id",
            "created_at",
            "name",
        ]


class ServiceSalonInputSerializer(serializers.ModelSerializer):
    price = MoneyField()

    class Meta:
        model = models.ServiceSalon
        fields = [
            "salon",
            "service",
            "price",
        ]

    # def __init__(self, *args, **kwargs):
    #     many = kwargs.pop('many', True)
    #     super(ServiceSalonInputSerializer, self).__init__(
    #         many=many, *args, **kwargs)


class ServiceSalonSerializer(serializers.ModelSerializer):
    price = MoneyField()

    class Meta:
        model = models.ServiceSalon
        fields = [
            "id",
            "service",
            "price",
        ]
        depth = 1
