from typing import Any

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..core.models import ModelWithMetadata, TimeStampedModel
from . import Gender


class Address(TimeStampedModel):
    address = models.CharField(
        max_length=512, blank=True, null=True, help_text="Địa chỉ cụ thể"
    )
    province = models.CharField(
        max_length=128, blank=True, null=True, help_text="Tỉnh/thành phố trực thuộc"
    )
    district = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Quận/huyện/thành phố không trực thuộc",
    )
    ward = models.CharField(
        max_length=128, blank=True, null=True, help_text="Phường/xã"
    )
    hamlet = models.CharField(
        max_length=128, blank=True, null=True, help_text="Thôn/xóm/ấp/đường"
    )
    lat = models.FloatField(blank=True, null=True, help_text="Vĩ độ")
    lng = models.FloatField(blank=True, null=True, help_text="Kinh độ")
    position_url = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        help_text="Url của vị trí trên google map",
    )

    def save(self, *args, **kwargs):
        self.address = (
            self.hamlet + ", " + self.ward + ", " + self.district + ", " + self.province
        )
        return super().save(*args, **kwargs)


class UserQueryset(models.QuerySet):
    def filter(self: models.QuerySet, *args: Any, **kwargs: Any) -> models.QuerySet:
        # if "type" is not in kwargs, default: hide orders with type RETURN
        if all(key.startswith("is_active") is False for key in kwargs.keys()):
            kwargs["is_active"] = True
        return super().filter(*args, **kwargs)

    def all(self) -> models.QuerySet:
        # Hidden type: RETURN
        return self.filter()


class UserManager(BaseUserManager):
    objects = UserQueryset.as_manager()


class BaseUser(AbstractUser, TimeStampedModel, ModelWithMetadata):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        blank=True,
        null=True,
    )
    email = models.EmailField(_("email address"), unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    avatar = models.URLField(max_length=512, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_completed_booking = models.PositiveIntegerField(default=0)
    is_salon = models.BooleanField(default=False)
    address = models.ForeignKey(
        Address, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )

    USERNAME_FIELD = "username"

    class Meta:
        ordering = ("date_joined",)

    @property
    def fcm_tokens(self):
        return self.get_value_from_private_metadata("fcm_tokens", [])

    def store_fcm_token(self, fcm_token):
        fcm_tokens = self.fcm_tokens
        fcm_tokens.insert(0, fcm_token)
        self.store_value_in_private_metadata({"fcm_tokens": fcm_tokens})
        self.save(update_fields=("private_metadata",))


# class User(BaseUser):
#     gender = models.CharField(
#         max_length=6, choices=Gender.choices, blank=True, null=True
#     )

#     class Meta:
#         ordering = ("date_joined",)


class Salon(BaseUser):
    salon_name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    background_image = models.CharField(max_length=256, null=True, blank=True)
    total_reviews = models.IntegerField(default=0)
    vote_rate = models.FloatField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    description = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        ordering = ("date_joined",)
