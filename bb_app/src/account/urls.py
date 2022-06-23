from django.urls import include, path
from rest_framework.routers import DefaultRouter
# from service import views as service_views

from .views import AccountStoreFCMToken
# from .views import salon as salon_views
from .views import user as user_views

router = DefaultRouter()

router.register("users", user_views.UserViewSet)
# router.register("salons", salon_views.SalonViewSet)

# router.register("salonServices", service_views.ServiceSalonViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # apis for salon
    # path("salonAddress/", salon_views.AddressUpdate.as_view()),
    # path("salonBookings/", salon_views.SalonViewSet.as_view({"get": "bookings"})),
    path("userBookings/", user_views.UserViewSet.as_view({"get": "bookings"})),
    # path("fcmToken/", AccountStoreFCMToken.as_view())
    # apis for user
]
