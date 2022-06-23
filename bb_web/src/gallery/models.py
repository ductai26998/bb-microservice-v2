from django.db import models

from ..account.models import Salon
from ..core.models import Photo, TimeStampedModel


class Gallery(TimeStampedModel):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name="gallery")

    class Meta:
        ordering = ("-created_at",)


class GalleryPhoto(Photo):
    gallery = models.ForeignKey(
        Gallery, on_delete=models.CASCADE, related_name="photos"
    )
