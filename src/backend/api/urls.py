from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import UserRegisterAPIView, UserLoginAPIView

urlpatterns = [
    path('user/token/', TokenObtainPairView.as_view(), name='user_token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='user_token_refresh'),
    path('user/token/verify/', TokenVerifyView.as_view(), name='user_token_verify'),
    path('user/register/', UserRegisterAPIView.as_view(), name='user_register'),
    path('user/login/', UserLoginAPIView.as_view(), name='user_login'),
]