from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Dream, DreamMessage, UserDevice, Analysis
from .serializers import UserSerializer, SubscriptionSerializer, UserDeviceSerializer, DreamSerializer, DreamMessageSerializer, AnalysisSerializer
from django.contrib.auth import authenticate
from ipware import get_client_ip
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from django.conf import settings
from django.utils import timezone

# Create your views here.

#  New Branch Test  #

## ../api/user/register/ -> POST
class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            registered_user = serializer.save()
            client_ip, is_routable = get_client_ip(request)
            UserDevice.objects.create(user=registered_user, device_ip=client_ip, is_active=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
## ../api/user/login/ -> POST
class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, email=email, password=password)
        
        if not user:
            return Response({'error': 'Password or email is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
        
        client_ip, is_routable = get_client_ip(request)
        device_object = UserDevice.objects.filter(user=user, device_ip=client_ip).exists()
        if not device_object:
            UserDevice.objects.create(user=user, device_name="New Device", device_ip=client_ip, is_active=True)

        refresh = RefreshToken.for_user(user=user)
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            }
        }, status=status.HTTP_200_OK)
    
## ../api/user/google-login/ -> POST
class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def post(self, request):
        try:
            # Evet, buradaki token sadece Google ile giriş işlemi sırasında kullanıcının kimliğini doğrulamak için kullanılıyor.
            # Uygulama içerisinde başka bir yerde bu tokeni kullanmayacaksın.
            token = request.data.get('token')
            
            if not token:
                return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )

            google_user_id = idinfo['sub']
            email = idinfo['email']
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')

            try:
                user = User.objects.get(email=email)
                user.google_id = google_user_id
                if picture:
                    user.image = picture
                user.save()
            except User.DoesNotExist:
                username = email.split('@')[0]
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    google_id=google_user_id,
                    image=picture,
                    password=None
                )

            client_ip, is_routable = get_client_ip(request)
            device_object = UserDevice.objects.filter(user=user, device_ip=client_ip).exists()
            if not device_object:
                UserDevice.objects.create(
                    user=user, 
                    device_name="Google Login Device", 
                    device_ip=client_ip, 
                    is_active=True
                )

            refresh = RefreshToken.for_user(user=user)
            print("refresh: "+str(refresh))
            print("access: "+str(refresh.access_token))
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "image": user.image,
                }
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({'error': 'Google login failed', 'error_message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
## ../api/user/google-token-refresh/ -> POST
class GoogleTokenRefreshView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def post(self, request):
        google_id_token = request.data.get('token')
        if not google_id_token:
            return Response({'error': 'Google ID token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idinfo = id_token.verify_oauth2_token(
                google_id_token,
                google_requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )
        except ValueError:
            return Response({'error': 'Invalid or expired Google ID token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Google token verification failed', 'error_message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        google_user_id = idinfo.get('sub')
        email = idinfo.get('email')
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')

        if not email or not google_user_id:
            return Response({'error': 'Google token did not contain expected claims'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, google_id=google_user_id)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=email)
                user.google_id = google_user_id
                if picture:
                    user.image = picture
                user.save()
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "image": user.image,
            }
        }, status=status.HTTP_200_OK)
    
## ../api/user/me/ -> GET
class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
## ../api/user/me/dreams/ -> GET
class UserDreamListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def get(self, request):
        user = request.user
        dreams = Dream.objects.filter(author=user).order_by('-created_at')
        serializer = DreamSerializer(dreams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

## ../api/user/me/dream/create/ -> POST
class UserDreamCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def post(self, request):
        user = request.user
        user_object = get_object_or_404(User, id=user.id)
        if not user_object.can_send_chat():
            return Response({'error': 'You have reached the maximum number of dreams'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DreamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
## ../api/user/me/dreams/<int:id>/ -> GET
class UserDreamChatAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]
    
    def get(self, request, id):
        dream_messages = DreamMessage.objects.filter(dream_id=id).order_by('created_at')
        serializer = DreamMessageSerializer(dream_messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)