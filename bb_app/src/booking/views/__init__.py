from functools import reduce

from ...account import models as account_models
# from account.serializers.salon import SalonReviewSerializer
from ...core.views import BaseViewSet
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .. import BookingErrorCode, BookingStatus, models
from ..serializers import (
    BookingCreateInputSerializer,
    BookingReviewInputSerializer,
    BookingSerializer,
)
# from ..tasks import notifications as nf


class BookingViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]

    queryset = models.Booking.objects.filter()
    serializer_class = BookingSerializer
    serializer_map = {
        "create": BookingCreateInputSerializer,
    }

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            data = request.data
            salon_id = data["salon_id"]
            service_ids = data["service_ids"]
            salon = account_models.Salon.objects.filter(id=salon_id).first()
            if not salon:
                return Response(
                    {
                        "code": BookingErrorCode.NOT_FOUND,
                        "messages": "The salon %s is not found" % salon_id,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            salon_services = salon.services.filter(service__in=service_ids)
            for service_id in service_ids:
                if service_id not in [
                    str(salon_service.service.id) for salon_service in salon_services
                ]:
                    return Response(
                        {
                            "code": BookingErrorCode.NOT_FOUND,
                            "messages": "The salon has not a service with id=%s"
                            % service_id,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            total_net_amount = reduce(
                lambda x, y: x + y,
                [salon_service.price_amount for salon_service in salon_services],
                0,
            )
            booking = models.Booking.objects.create(
                user_id=user.id, salon=salon, total_net_amount=total_net_amount
            )
            booking_services = []

            for salon_service in salon_services:
                booking_services.append(
                    models.BookingService(
                        booking=booking,
                        service=salon_service.service,
                        price=salon_service.price,
                    )
                )
            models.BookingService.objects.bulk_create(booking_services)
            nf.send_notify_to_user_about_booking_placed(booking)
            response = BookingSerializer(booking)
            return Response(
                {
                    "detail": "Create booking successful",
                    "data": response.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "code": BookingErrorCode.PROCESSING_ERROR,
                    "detail": "Create booking failed",
                    "messages": e.args,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        booking = self.get_object()
        if request.user.id not in [booking.salon_id, booking.user_id]:
            return Response(
                {
                    "code": BookingErrorCode.PERMISSION_DENIED,
                    "detail": "Permission denied",
                    "messages": "Permission denied",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def confirm(self, request, *args, **kwargs):
        """
        Confirm the booking
        """
        booking = self.get_object()
        if booking.salon_id != request.user.id:
            return Response(
                {
                    "code": BookingErrorCode.PERMISSION_DENIED,
                    "detail": "Permission denied",
                    "messages": "Permission denied",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if booking.status != BookingStatus.NEW:
            return Response(
                {
                    "code": BookingErrorCode.INVALID,
                    "detail": "The booking status must be '%s'" % BookingStatus.NEW,
                    "messages": "The booking status must be '%s'" % BookingStatus.NEW,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = BookingStatus.CONFIRMED
        booking.updated_at = timezone.now()
        booking.save(update_fields=["status", "updated_at"])
        nf.send_notify_to_user_about_booking_confirmed(booking)
        response = BookingSerializer(booking)
        return Response(
            {
                "detail": "Confirm booking successful",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, *args, **kwargs):
        """
        Cancel the booking
        """
        booking = self.get_object()
        if request.user.id not in [booking.salon_id, booking.user_id]:
            return Response(
                {
                    "code": BookingErrorCode.PERMISSION_DENIED,
                    "detail": "Permission denied",
                    "messages": "Permission denied",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if booking.status not in [BookingStatus.NEW, BookingStatus.CONFIRMED]:
            return Response(
                {
                    "code": BookingErrorCode.INVALID,
                    "detail": "The booking status must be '%s'" % BookingStatus.NEW,
                    "messages": "The booking status must be '%s'" % BookingStatus.NEW,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = BookingStatus.CANCELED
        booking.updated_at = timezone.now()
        booking.save(update_fields=["status", "updated_at"])
        if request.user.id == booking.salon_id:
            nf.send_notify_to_salon_about_booking_canceled_by_salon(booking)
        elif request.user.id == booking.user_id:
            nf.send_notify_to_salon_about_booking_canceled_by_user(booking)
        response = BookingSerializer(booking)
        return Response(
            {
                "detail": "Cancel booking successful",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="requestToComplete")
    def request_to_complete(self, request, *args, **kwargs):
        """
        Salon sends request to user to complete the booking
        """
        booking = self.get_object()
        if booking.salon_id != request.user.id:
            return Response(
                {
                    "code": BookingErrorCode.PERMISSION_DENIED,
                    "detail": "Permission denied",
                    "messages": "Permission denied",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if booking.status != BookingStatus.CONFIRMED:
            return Response(
                {
                    "code": BookingErrorCode.INVALID,
                    "detail": "The booking status must be '%s'"
                    % BookingStatus.CONFIRMED,
                    "messages": "The booking status must be '%s'"
                    % BookingStatus.CONFIRMED,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = BookingStatus.REQUEST_TO_COMPLETE
        booking.updated_at = timezone.now()
        booking.save(update_fields=["status", "updated_at"])
        nf.send_notify_to_salon_about_booking_requested_to_complete(booking)
        response = BookingSerializer(booking)
        return Response(
            {
                "detail": "Sent request to the user to complete booking successfully",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="markAsCompleted")
    def mark_as_completed(self, request, *args, **kwargs):
        """
        User confirms that the booking was completed
        """
        booking = self.get_object()
        if booking.user_id != request.user.id:
            return Response(
                {
                    "code": BookingErrorCode.PERMISSION_DENIED,
                    "detail": "Permission denied",
                    "messages": "Permission denied",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if booking.status != BookingStatus.REQUEST_TO_COMPLETE:
            return Response(
                {
                    "code": BookingErrorCode.INVALID,
                    "detail": "The booking status must be '%s'"
                    % BookingStatus.REQUEST_TO_COMPLETE,
                    "messages": "The booking status must be '%s'"
                    % BookingStatus.REQUEST_TO_COMPLETE,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = BookingStatus.COMPLETED
        booking.updated_at = timezone.now()
        booking.save(update_fields=["status", "updated_at"])
        nf.send_notify_to_salon_about_booking_completed(booking)
        response = BookingSerializer(booking)
        return Response(
            {
                "detail": "Booking was completed",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def review(self, request, *args, **kwargs):
        """
        User add review about the salon
        """
        booking = self.get_object()
        salon = booking.salon
        requester = request.user
        if requester.is_anonymous:
            return Response(
                {
                    "code": BookingErrorCode.PERMISSION_DENIED,
                    "detail": "Anonymous user can not review salon",
                    "messages": "Anonymous user can not review salon",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if requester.id == salon.id:
            return Response(
                {
                    "code": BookingErrorCode.INVALID_ACTION,
                    "detail": "You can not review yourself",
                    "messages": "You can not review yourself",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid_statuses = [BookingStatus.COMPLETED, BookingStatus.REQUEST_TO_COMPLETE]
        if booking.status not in valid_statuses:
            return Response(
                {
                    "code": BookingErrorCode.INVALID_ACTION,
                    "detail": "Booking status must be: %s" % valid_statuses,
                    "messages": "Booking status must be: %s" % valid_statuses,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if booking.rating:
            return Response(
                {
                    "code": BookingErrorCode.INVALID_ACTION,
                    "detail": "This booking was reviewed before",
                    "messages": "This booking was reviewed before",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        serializer = BookingReviewInputSerializer(data=data)
        if serializer.is_valid():
            rating = data["rating"]
            booking.rating = rating
            booking.review = data.get("review")
            update_fields = ["rating", "review"]
            if booking.status == BookingStatus.REQUEST_TO_COMPLETE:
                booking.status = BookingStatus.COMPLETED
                update_fields.append("status")
                nf.send_notify_to_salon_about_booking_completed(booking)
            total_reviews = salon.total_reviews
            vote_rate = salon.vote_rate
            if vote_rate is None:
                vote_rate = 0
            salon.vote_rate = round((vote_rate * total_reviews + rating) / (total_reviews + 1), 3)
            salon.total_reviews = total_reviews + 1
            salon.save(update_fields=["vote_rate", "total_reviews"])
            booking.save(update_fields=update_fields)
            response = SalonReviewSerializer(booking)
            return Response(
                {
                    "data": response.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "code": BookingErrorCode.PROCESSING_ERROR,
                "detail": "Can not add review",
                "messages": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
