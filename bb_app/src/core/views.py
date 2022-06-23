from django.core.exceptions import ValidationError
from rest_framework import status, views, viewsets
from rest_framework.response import Response

from . import CoreErrorCode


class BaseViewSet(viewsets.ModelViewSet):
    serializer_class = None
    required_alternate_scopes = {}
    serializer_map = {}
    permission_map = {}

    def get_serializer_class(self):
        return self.serializer_map.get(self.action, self.serializer_class)

    def get_permissions(self):
        return [
            permission()
            for permission in self.permission_map.get(
                self.action, self.permission_classes
            )
        ]

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response(
                {
                    "detail": kwargs.get("success_detail"),
                    "data": response.data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "detail": kwargs.get("fail_detail"),
                    "code": kwargs.get("code"),
                    "messages": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(
            {
                "detail": kwargs.get("success_detail"),
                "data": response.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
            return Response(
                {
                    "detail": kwargs.get("success_detail"),
                    "data": response.data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "detail": kwargs.get("fail_detail"),
                    "code": CoreErrorCode.NOT_FOUND,
                    "messages": e.args,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response(
                {
                    "detail": kwargs.get("success_detail"),
                    "data": response.data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "detail": kwargs.get("fail_detail"),
                    "code": kwargs.get("code"),
                    "messages": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return Response(
                {
                    "detail": kwargs.get("success_detail"),
                    "data": response.data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "detail": kwargs.get("fail_detail"),
                    "code": CoreErrorCode.NOT_FOUND,
                    "messages": e.args,
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class BaseAPIView(views.APIView):
    @classmethod
    def get_instance(self, request, **kwargs):
        instance = request.user
        if instance.is_anonymous:
            raise ValidationError("Permission denied", code="Error")
        return instance

    @classmethod
    def post(self, request, **kwargs):
        self.get_instance(request, **kwargs)
