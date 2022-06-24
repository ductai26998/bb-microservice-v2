from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf.urls import url
from ..service import views as service_views
from .views import AccountStoreFCMToken
from .views import salon as salon_views
from .views import user as user_views

router = DefaultRouter()

# router.register("users", user_views.users, basename="users")
router.register("salons", salon_views.SalonViewSet)

router.register("salonServices", service_views.ServiceSalonViewSet)

urlpatterns = [
    # url(r'^(?P<pk>\d+)/$', views.index, name='test_regex'),
    path("", include(router.urls)),
    # apis for salon
    path("salonAddress/", salon_views.AddressUpdate.as_view()),
    path("salonBookings/", salon_views.SalonViewSet.as_view({"get": "bookings"})),
    # path("userBookings/", user_views.UserViewSet.as_view({"get": "bookings"})),
    path("fcmToken/", AccountStoreFCMToken.as_view()),
    # apis for user
    url(r"users/$", user_views.UsersView.as_view(), name="users"),
    path("users/<pk>/", user_views.UserDetailView.as_view(), name="user-details"),
]
