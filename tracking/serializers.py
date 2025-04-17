from rest_framework import serializers
from .models import User, Location
from django.contrib.auth import authenticate

# -----------------------------
# Serializer dùng cho ĐĂNG KÝ
# -----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        """Tạo user mới với hashed password"""
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

# -----------------------------
# Serializer dùng cho ĐĂNG NHẬP
# -----------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """Xác thực tài khoản từ username & password"""
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")

# --------------------------------------
# Serializer dùng cho CẬP NHẬT VỊ TRÍ
# --------------------------------------
class LocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['latitude', 'longitude']

# ---------------------------------------------------
# Serializer dùng cho XEM VỊ TRÍ của user (bao gồm avatar)
# ---------------------------------------------------
class LocationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    avatar = serializers.CharField(source='user.avatar')  # Đường dẫn ảnh avatar của user

    class Meta:
        model = Location
        fields = ['user', 'latitude', 'longitude', 'timestamp', 'avatar']
