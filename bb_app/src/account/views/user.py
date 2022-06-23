from ..serializers.user import UserUpdateSerializer
from ...core.services.cloudinary import CloudinaryService
from ...core.views import BaseAPIView, BaseViewSet
from ...booking.serializers import BookingSerializer
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers import (
    UserRegisterInputSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from . import AccountErrorCode, models


class UserViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]

    serializer_map = {
        "list": UserSerializer,
        "retrieve": UserSerializer,
        "partial_update": UserUpdateSerializer,
    }
    permission_map = {
        "list": [IsAdminUser],
        "retrieve": [IsAuthenticated],
        "destroy": [IsAdminUser],
    }

    queryset = models.User.objects.filter()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get("q", "")
        query = (
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(phone_number__icontains=search_query)
            | Q(username__icontains=search_query)
        )
        self.queryset = models.User.objects.filter(query)
        return super().list(request, *args, **kwargs)

    def create(self, request):
        response = {
            "code": AccountErrorCode.NOT_FOUND,
            "detail": "Create function is not offered in this path.",
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        if str(request.user.id) != pk:
            response = {
                "code": AccountErrorCode.PERMISSION_DENIED,
                "detail": "Permission denied",
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        avatar = request.FILES.get("avatar")
        if avatar:
            avatar_folder_path = settings.CLOUDINARY_AVATAR_USER_FOLDER + str(pk) + "/"
            url = CloudinaryService.upload_image(avatar, avatar_folder_path)
            request.data["avatar"] = url
        return super().partial_update(request, pk)

    def destroy(self, request, pk=None):
        try:
            user = models.User.objects.get(pk=pk)
            if not user:
                return Response(
                    {
                        "code": AccountErrorCode.INACTIVE,
                        "detail": "User is inactive",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.is_active = False
            user.save()
            return Response(
                {
                    "detail": "User is deactivated successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "code": AccountErrorCode.PROCESSING_ERROR,
                    "detail": "Deactivation failed",
                    "messages": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
                exception=e,
            )

    @action(detail=True)
    def bookings(self, request, *args, **kwargs):
        """
        Returns a list of all the bookings that the given
        user belongs to.
        """
        requester_id = request.user.id
        user = models.User.objects.filter(id=requester_id).first()
        if not user:
            return Response(
                {
                    "code": AccountErrorCode.NOT_FOUND,
                    "detail": "User %s is not exist" % requester_id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        search_query = request.query_params.get("status", "")
        bookings = user.bookings.all()
        if search_query:
            bookings = bookings.filter(status=search_query)
        data = [BookingSerializer(booking).data for booking in bookings]
        response_dict = {
            "detail": None,
            "data": data,
            "error": None,
        }
        return Response(response_dict)


class UserRegister(BaseAPIView):
    @transaction.atomic
    def post(self, request):
        try:
            data = request.data
            serializer = UserRegisterInputSerializer(data=data)
            if serializer.is_valid():
                serializer.validated_data
                serializer.save()
                email = serializer.data["email"]
                account = models.User.objects.get(email=email)
                token = RefreshToken.for_user(account)
                response = UserRegisterSerializer(account)
                return Response(
                    {
                        "detail": "Registration successfully, check email to get otp",
                        "data": {
                            **response.data,
                            "access_token": str(token.access_token),
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "code": AccountErrorCode.PROCESSING_ERROR,
                    "detail": "Register user failed",
                    "messages": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "code": AccountErrorCode.PROCESSING_ERROR,
                    "detail": "Register user failed",
                    "messages": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
