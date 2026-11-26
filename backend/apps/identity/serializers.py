from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ("username","password","first_name","last_name","email","display_name")
    def create(self, validated_data): return User.objects.create_user(**validated_data)
class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username","first_name","last_name","email","display_name","role","is_active")
class LibraryTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user); token["role"] = user.role; token["username"] = user.username; return token
    def validate(self, attrs):
        data = super().validate(attrs); data["user"] = MeSerializer(self.user).data; return data
