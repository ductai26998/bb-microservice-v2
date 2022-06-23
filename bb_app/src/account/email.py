import random
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail

from . import models


def send_otp_to_email(user: models.BaseUser, email: str):
    subject = "Mã xác thực tài khoản Baber Booking"
    otp = str(random.randint(100000, 999999))
    message = "Mã xác thực của bạn là %s. Vui lòng không tiết lộ mã trên cho bất kỳ người nào. Xin cảm ơn." % otp
    from_email = settings.EMAIL_HOST
    try:
        send_mail(subject, message, from_email, [email])
    except Exception as e:
        print(e)
        return
    user.otp = otp
    user.save()
