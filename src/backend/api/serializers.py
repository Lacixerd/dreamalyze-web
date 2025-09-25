from rest_framework import serializers
from .models import User, Subscription, UserCredits, UserDevice, Dream, DreamMessage, Analysis, ProductPlan
from django.utils import timesince, timezone
import datetime

class UserSerializer(serializers.ModelSerializer):
    class UserCreditsSerializer(serializers.ModelSerializer):
        class Meta:
            model = UserCredits
            fields = ['total_amount', 'credit_type', 'amount']

    credits = UserCreditsSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'is_active',
            'user_plan',
            'watched_ads',
            'image',
            'google_id',
            'last_chat_at',
            'user_created_at',
            'user_updated_at',
            'user_deleted_at',
            'credits'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'user_plan': {'read_only': True},
            'user_created_at': {'read_only': True},
            'user_updated_at': {'read_only': True},
            'image': {'read_only': True},
            'google_id': {'read_only': True},
        }
    
    def create(self, validated_data: dict):
        validated_data.pop('user_plan')
        validated_data.pop('credits')
        free_plan = ProductPlan.objects.get(plan="Free")
        user = User.objects.create_user(user_plan=free_plan, **validated_data)
        return user
    
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only':True},
        }

class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }

class DreamMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DreamMessage
        fields = ['role', 'content']

class DreamSerializer(serializers.ModelSerializer):
    messages = DreamMessageSerializer(read_only=True, many=True)

    author = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Dream
        fields = ['id', 'author', 'title', 'description', 'created_at', 'updated_at', 'deleted_at', 'is_active', 'messages']
        extra_kwargs = {
            'id': {'read_only': True},
        }

class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }