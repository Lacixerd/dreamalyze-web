from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Dream, DreamMessage, UserDevice, Analysis, AIAnswer, UserCredits, ProductPlan
from .serializers import UserSerializer, SubscriptionSerializer, UserDeviceSerializer, DreamSerializer, DreamMessageSerializer, AnalysisSerializer
from django.contrib.auth import authenticate
from ipware import get_client_ip
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from django.conf import settings
from django.utils import timezone
from pprint import pprint

# Create your views here.

## ../api/user/register/ -> POST
class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            registered_user = serializer.save()
            client_ip, is_routable = get_client_ip(request)
            free_credit_plan = ProductPlan.objects.get(plan="Free")
            max_credit_amount = free_credit_plan.max_credit_amount
            UserDevice.objects.create(user=registered_user, device_ip=client_ip, is_active=True)
            UserCredits.objects.create(user=registered_user, credit_type=free_credit_plan, total_amount=max_credit_amount, amount=max_credit_amount)
            updated_serializer = UserSerializer(registered_user)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
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
        user.update_last_login()

        serializer = UserSerializer(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": serializer.data
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
                
                free_plan = ProductPlan.objects.get(plan='Free')

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    google_id=google_user_id,
                    image=picture,
                    password=None,
                    user_plan=free_plan
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

            serializer = UserSerializer(user)

            refresh = RefreshToken.for_user(user=user)
            print("refresh: "+str(refresh))
            print("access: "+str(refresh.access_token))
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serializer.data
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

        serializer = UserSerializer(user)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": serializer.data
        }, status=status.HTTP_200_OK)
    
## ../api/user/me/ -> GET
class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
## ../api/user/me/dreams/ -> GET, POST
class UserDreamListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def get(self, request):
        user = request.user
        dreams = Dream.objects.filter(author=user).order_by('-created_at')
        serializer = DreamSerializer(dreams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # TODO: Burası ilk mesajın database'e kaydedileceği kısımdır. Şuanlık sadece deneme amaçlı böyle bir şey yaptım
    def post(self, request):
        user = request.user
        user_object = get_object_or_404(User, id=user.id)
        if user_object.credits.amount > 0:
            user_object.credits.update_current_credits()
            serializer = DreamSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Your credit is insufficient"})
    
## ../api/user/me/dream/<uuid:id>/messages/ -> GET, POST
class UserDreamChatAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer]

    def get_queryset(self, user, id):
        dream = get_object_or_404(Dream, id=id, author=user)
        queryset = DreamMessage.objects.filter(dream=dream).order_by('created_at')
        serializer = DreamMessageSerializer(queryset, many=True)
        return serializer
    
    def get(self, request, id):
        user = request.user
        queryset = self.get_queryset(user=user, id=id)
        return Response(queryset.data, status=status.HTTP_200_OK)
    
    # TODO: Burası ilk mesajdan sonraki mesajların yazılacağı kısımlardır.
    def post(self, request, id):
        user = request.user
        user_dreams = Dream.objects.filter(author=user, id=id)
        if not user_dreams:
            return Response({"error": "Unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)
        dream_messages = DreamMessage.objects.filter(dream_id=id)
        if not dream_messages:
            return Response({"error": "This endpoint cannot be used to post the first message"})
        serializer = DreamMessageSerializer(data=request.data)
        if serializer.is_valid():
            user_message = serializer.save(dream_id=id)

            # TODO: Buraya AI analiz fonksiyonu gelecek. user_message yapay zekaya gönderilecek
            ai_response = "None"

            analyst_message = DreamMessage.objects.create(
                dream_id=id,
                role="analyst",
                message=ai_response
            )

            return Response({
                "analyst": DreamMessageSerializer(analyst_message).data,
                "user": DreamMessageSerializer(user_message).data
            }, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
