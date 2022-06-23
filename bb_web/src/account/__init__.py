from django.db import models

from ..core import CoreErrorCode


class Gender(models.TextChoices):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class AccountErrorCode(CoreErrorCode):
    INACTIVE = "inactive"
