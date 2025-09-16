from rest_framework import serializers
from .models import User, Subscription, UserDevice, Dream, DreamMessage, Analysis

class UserSerializer(serializers.ModelSerializer):
    # dreams = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='user_dream_list'
    # )

    class Meta:
        model = User
        fields = '__all__'
        # fields = ['id', 'username', 'email', 'is_active', 'user_created_at', 'user_updated_at', 'user_plan', 'last_chat_at', 'next_available_chat_at', 'ip_address']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'user_created_at': {'read_only': True},
            'user_updated_at': {'read_only': True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
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

class DreamSerializer(serializers.ModelSerializer):
    # chat_messages = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='user_dream_chat'
    # )

    author = serializers.StringRelatedField()
    class Meta:
        model = Dream
        # fields = '__all__'
        fields = ['id', 'author', 'created_at', 'updated_at', 'deleted_at','is_active']
        extra_kwargs = {
            'id': {'read_only': True},
        }

class DreamMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DreamMessage
        fields = '__all__'

class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }