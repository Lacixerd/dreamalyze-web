from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import UserRegisterAPIView, UserLoginAPIView, UserDreamListAPIView, UserProfileAPIView, UserDreamCreateAPIView, UserDreamChatAPIView

urlpatterns = [
    path('user/register/', UserRegisterAPIView.as_view(), name='user_register'),
    path('user/login/', UserLoginAPIView.as_view(), name='user_login'),
    path('user/token/', TokenObtainPairView.as_view(), name='user_token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='user_token_refresh'),
    path('user/token/verify/', TokenVerifyView.as_view(), name='user_token_verify'),

    path('user/me/', UserProfileAPIView.as_view(), name='user_profile'), ## GET
    path('user/me/dreams/', UserDreamListAPIView.as_view(), name='user_dream_list'), ## GET
    path('user/me/dreams/create/', UserDreamCreateAPIView.as_view(), name='user_dream_create'), ## POST
    path('user/me/dreams/<int:id>/', UserDreamChatAPIView.as_view(), name='user_dream_chat'), ## GET
]