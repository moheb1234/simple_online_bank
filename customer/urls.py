from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path('signup/', signup),
    path('login/', login),
    path('verify-code/<int:code>/', verify_code)
]
