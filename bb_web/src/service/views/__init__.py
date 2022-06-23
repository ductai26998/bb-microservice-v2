from django.contrib.auth.hashers import check_password
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...account import models as account_models
from ...core.views import BaseAPIView, BaseViewSet
from .. import ServiceErrorCode, models
from ..serializers import (
    ServiceInputSerializer,
    ServiceSalonInputSerializer,
    ServiceSalonSerializer,
    ServiceSerializer,
)


class ServiceViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]

    queryset = models.Service.objects.filter()
    serializer_class = ServiceSerializer
    serializer_map = {
        "create": ServiceInputSerializer,
    }

    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get("q", "")
        self.queryset = models.Service.objects.filter(name__icontains=search_query)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            account = request.user
            data = request.data
            price = data.pop("price")
            name = data.get("name")
            service_exist = models.Service.objects.filter(name__iexact=name).exists()
            if service_exist:
                return Response(
                    {
                        "code": ServiceErrorCode.EXISTED,
                        "messages": "Service existed",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # data["price"] = price
            serializer = ServiceInputSerializer(data=data)
            if serializer.is_valid():
                service = serializer.save()
                service_salon_object = models.ServiceSalon.objects.create(
                    service=service,
                    salon_id=account.id,
                    price_amount=price.get("amount"),
                    currency=price.get("currency"),
                )
                service_salon = ServiceSalonInputSerializer(service_salon_object)
                return Response(
                    {
                        "detail": "Success add a new service",
                        "data": service_salon.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "code": ServiceErrorCode.PROCESSING_ERROR,
                    "messages": "Add new service failed",
                    "errors": serializer._errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                exception=serializer._errors,
            )
        except Exception as e:
            return Response(
                {
                    "code": ServiceErrorCode.PROCESSING_ERROR,
                    "messages": "Add new service failed",
                    "errors": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
                exception=e,
            )

    def partial_update(self, request, pk=None):
        response = {
            "code": ServiceErrorCode.NOT_FOUND,
            "messages": "Partial update function is not offered in this path.",
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        response = {
            "code": ServiceErrorCode.NOT_FOUND,
            "messages": "Update function is not offered in this path.",
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ServiceSalonViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]

    queryset = models.ServiceSalon.objects.filter()
    # serializer_class = ServiceSalonInputSerializer
    serializer_map = {
        "list": ServiceSalonSerializer,
        "retrieve": ServiceSalonSerializer,
    }

    def list(self, request, *args, **kwargs):
        salon = request.user
        self.queryset = models.ServiceSalon.objects.filter(salon_id=salon.id)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # account = request.user
        # request.data["salon"] = account.id
        # return super().create(request, *args, **kwargs)

        try:
            account = request.user
            services = request.data
            for service_infor in services:
                service_id = service_infor.get("service")
                service_in_salon = models.ServiceSalon.objects.filter(
                    salon_id=account.id, service_id=service_id
                ).first()
                if service_in_salon:
                    return Response(
                        {
                            "code": ServiceErrorCode.EXISTED,
                            "messages": "Service '%s' existed"
                            % service_in_salon.service.name,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                service_exist = models.Service.objects.filter(id=service_id).exists()
                if not service_exist:
                    return Response(
                        {
                            "code": ServiceErrorCode.NOT_FOUND,
                            "messages": "Service doesn't exist",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                price = service_infor.get("price")
                if not price:
                    return Response(
                        {
                            "code": ServiceErrorCode.REQUIRED,
                            "messages": "Price is required",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                models.ServiceSalon.objects.create(
                    service_id=service_id,
                    salon_id=account.id,
                    price_amount=price.get("amount"),
                    currency=price.get("currency"),
                )
            return Response(
                {
                    "detail": "Success add service into salon",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "code": ServiceErrorCode.PROCESSING_ERROR,
                    "messages": "Add new service failed",
                    "errors": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
                exception=e,
            )

    def partial_update(self, request, pk=None):
        instance = self.get_object()
        data = request.data
        price = data.pop("price")
        data["price_amount"] = price["amount"]
        print(data)
        if request.user.id != instance.salon_id:
            return Response(
                {
                    "code": ServiceErrorCode.PERMISSION_DENIED,
                    "messages": "Permission denied",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(
            request,
            pk=pk,
            code=ServiceErrorCode.INVALID,
            fail_detail="Update service was failed",
            success_detail="Update service successfully",
        )

    def update(self, request, pk=None):
        response = {
            "code": ServiceErrorCode.NOT_FOUND,
            "messages": "Update function is not offered in this path.",
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        return super().destroy(
            request,
            pk,
            success_detail="Delete service successfully",
            fail_detail="Can not delete this service",
        )
