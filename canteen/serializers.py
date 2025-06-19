from rest_framework import serializers
from .models import User , menu , Vote
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    address = serializers.JSONField(required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name','username', 'email','address', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_address(self, value):
        required_keys = ['street', 'city', 'country', 'zipcode']
        if not isinstance(value, dict):
            raise serializers.ValidationError("Address must be a dictionary.")
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"'{key}' is required in address.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(

            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            address=validated_data.get('address', {}),
            role=validated_data['role']
           
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = menu
        fields=['id','date','dishes', 'max_capacity']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'user', 'menu', 'will_attend', 'voted_at']
        read_only_fields = ['user', 'voted_at']