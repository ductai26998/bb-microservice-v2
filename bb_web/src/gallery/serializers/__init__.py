from rest_framework import serializers

from .. import models


class GalleryPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GalleryPhoto
        fields = [
            "id",
            "url",
        ]


class GallerySerializer(serializers.ModelSerializer):
    photos = GalleryPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Gallery
        fields = [
            "id",
            "photos",
        ]
        depth = 1
