import requests

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView

class UsersView(ListAPIView):
    def get(self, request, *args, **kwargs):
        id=self.kwargs.get('pk')
        response = requests.get(settings.APP_URL + "/users/")
        if response.ok:
            return Response(
                response.json(),
                status=status.HTTP_200_OK,
            )
        return Response(
            response.json(),
            status=status.HTTP_400_BAD_REQUEST,
        )

class UserDetailView(RetrieveAPIView):
    def get(self, request, pk, *args, **kwargs):
        response = requests.get(settings.APP_URL + "/users/%s/" % pk)
        if response.ok:
            return Response(
                response.json(),
                status=status.HTTP_200_OK,
            )
        return Response(
            response.json(),
            status=status.HTTP_400_BAD_REQUEST,
        )
