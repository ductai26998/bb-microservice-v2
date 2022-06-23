"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]


from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .account.views import LoginWithEmailOrUsername, VerifyOTP
# from .account.views import salon as salon_views
from .account.views import user as user_views

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    url("", include("src.account.urls")),
    # url("", include("src.service.urls")),
    url("", include("src.booking.urls")),
    # url("", include("notification.urls")),
    url("verifyOTP/", VerifyOTP.as_view(), name="verify_user"),
    url("login/", LoginWithEmailOrUsername.as_view(), name="login"),
    # apis for salon
    # url("registerSalon/", salon_views.SalonRegister.as_view(), name="register_salon"),
    # apis for user
    url("registerUser/", user_views.UserRegister.as_view(), name="register_user"),
]
