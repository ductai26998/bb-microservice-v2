from django.contrib.auth.hashers import check_password
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ...core.views import BaseAPIView
from .. import AccountErrorCode, models
from ..serializers import (
    AdminSerializer,
    SalonSerializer,
    # UserSerializer,
    VerifyAccountSerializer,
)
from ..utils.firebase import clean_up_user_fcm_tokens


class VerifyOTP(BaseAPIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            instance = super().get_instance(request)
            if instance.is_verified:
                return Response(
                    {
                        "code": AccountErrorCode.VERIFY_FAIL,
                        "detail": "User is verified before",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = request.data
            serializer = VerifyAccountSerializer(data=data)

            if serializer.is_valid():
                email = serializer.data["email"]
                otp = serializer.data["otp"]
                if instance.email != email:
                    return Response(
                        {
                            "code": AccountErrorCode.INVALID,
                            "detail": "Invalid email",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if instance.otp != otp:
                    return Response(
                        {
                            "code": AccountErrorCode.INVALID,
                            "detail": "OTP wrong",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                instance.is_verified = True
                instance.save()

                return Response(
                    {
                        "detail": "Verification successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "code": AccountErrorCode.VERIFY_FAIL,
                    "detail": "OTP verification failed",
                    "messages": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                exception=serializer.errors,
            )
        except Exception as e:
            return Response(
                {
                    "code": AccountErrorCode.VERIFY_FAIL,
                    "detail": "OTP verification failed",
                    "messages": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
                exception=e,
            )


class LoginWithEmailOrUsername(APIView):
    def post(self, request):
        try:
            mixin_id = request.data.get("mixin_id")
            password = request.data.get("password")

            account = models.BaseUser.objects.filter(username=mixin_id).first()
            if not account:
                account = models.BaseUser.objects.filter(email=mixin_id).first()
            if not account:
                return Response(
                    {
                        "code": AccountErrorCode.NOT_FOUND,
                        "detail": "Email or username is not exist",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            is_true_password = check_password(password, account.password)
            if not is_true_password:
                return Response(
                    {
                        "code": AccountErrorCode.VERIFY_FAIL,
                        "detail": "Password is wrong",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken.for_user(account)
            if account.is_salon:
                salon = models.Salon.objects.get(id=account.id)
                serializer = SalonSerializer(salon)
            elif account.is_superuser:
                serializer = AdminSerializer(account)
            else:
                user = models.User.objects.get(id=account.id)
                serializer = UserSerializer(user)
            return Response(
                {
                    "detail": "Login successfully",
                    "data": {
                        **serializer.data,
                        "access_token": str(token.access_token),
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "code": AccountErrorCode.VERIFY_FAIL,
                    "detail": "Login failed",
                    "messages": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
                exception=e,
            )


class AccountStoreFCMToken(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            current_user = request.user
            fcm_tokens = current_user.fcm_tokens
            fcm_token = request.data.get("fcm_token")
            if not fcm_token:
                return Response(
                    {
                        "code": AccountErrorCode.REQUIRED,
                        "detail": "fcm_token is not blank",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if fcm_token.strip() != "" and fcm_token not in fcm_tokens:
                current_user.store_fcm_token(fcm_token)
            if not clean_up_user_fcm_tokens(current_user):
                return Response(
                    {
                        "code": AccountErrorCode.INVALID,
                        "detail": "fcm_token invalid",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "detail": "Add fcm_token successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "code": AccountErrorCode.PROCESSING_ERROR,
                    "detail": "Can not add fcm_token",
                    "messages": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
