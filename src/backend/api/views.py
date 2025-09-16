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

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
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