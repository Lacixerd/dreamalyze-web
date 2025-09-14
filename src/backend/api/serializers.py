from rest_framework import serializers
from .models import User, Dream, DreamMessage, Interpretation

class UserSerializer(serializers.ModelSerializer):
    # dreams = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='dream-detail'
    # )

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'user_created_at': {'read_only': True},
            'user_updated_at': {'read_only': True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class DreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dream
        fields = '__all__'

class DreamMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DreamMessage
        fields = '__all__'

class InterpretationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interpretation
        fields = '__all__'