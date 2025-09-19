from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import (
    UserRegisterAPIView, UserLoginAPIView, UserDreamListCreateAPIView, 
    UserProfileAPIView, UserDreamChatAPIView,
    GoogleLoginAPIView, GoogleTokenRefreshView
)

urlpatterns = [
    path('user/register/', UserRegisterAPIView.as_view(), name='user_register'),
    path('user/login/', UserLoginAPIView.as_view(), name='user_login'),
    path('user/google-login/', GoogleLoginAPIView.as_view(), name='user_google_login'),
    path('user/google-token-refresh/', GoogleTokenRefreshView.as_view(), name='user_google_token_refresh'),
    path('user/token/', TokenObtainPairView.as_view(), name='user_token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='user_token_refresh'),
    path('user/token/verify/', TokenVerifyView.as_view(), name='user_token_verify'),

    path('user/me/', UserProfileAPIView.as_view(), name='user_profile'), ## GET
    path('user/me/dreams/', UserDreamListCreateAPIView.as_view(), name='user_dream_list'), ## GET, POST
    path('user/me/dream/<uuid:id>/messages/', UserDreamChatAPIView.as_view(), name='user_dream_chat'), ## GET
]