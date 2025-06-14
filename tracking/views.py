from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from .models import User, Location
from .serializers import RegisterSerializer, LoginSerializer, LocationSerializer, LocationCreateSerializer
from .forms import UpdateProfileForm

import os

User = get_user_model()

# ---------------------
# HTML Views
# ---------------------

def home_view(request):
    """Hiển thị trang chủ"""
    return render(request, 'tracking/home.html')


def login_view(request):
    """Đăng nhập qua form HTML"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'tracking/login.html', {'form': {'errors': True}})
    return render(request, 'tracking/login.html')


def register_view(request):
    """Đăng ký tài khoản mới"""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST.get('email', '')
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'tracking/register.html', {'error': 'Mật khẩu và xác nhận không khớp.'})

        if User.objects.filter(username=username).exists():
            return render(request, 'tracking/register.html', {'error': 'Tên người dùng đã tồn tại.'})

        user = User.objects.create_user(username=username, password=password, email=email)
        auth_login(request, user)
        return redirect('login')

    return render(request, 'tracking/register.html')


def map_view(request):
    """Hiển thị bản đồ người dùng"""
    return render(request, 'tracking/map.html')


@login_required
def profile_view(request):
    """Hiển thị & cập nhật avatar người dùng"""
    avatar_dir = os.path.join(os.path.dirname(__file__), 'static', 'tracking', 'avatar')
    avatars = os.listdir(avatar_dir)

    if request.method == 'POST':
        selected = request.POST.get('avatar')
        if selected in avatars:
            request.user.avatar = f'tracking/avatar/{selected}'
            request.user.save()
            return redirect('profile')

    return render(request, 'tracking/profile.html', {'avatars': avatars})


@login_required
def update_profile_view(request):
    """Cập nhật username / email người dùng"""
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công.')
            return redirect('profile')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại.')
    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, 'tracking/update_profile.html', {'form': form})


@login_required
def change_password_view(request):
    """Đổi mật khẩu người dùng"""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect('profile')
        else:
            messages.error(request, 'Có lỗi, vui lòng kiểm tra lại.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'tracking/change_password.html', {'form': form})


def logout_view(request):
    """Đăng xuất người dùng"""
    logout(request)
    return redirect('login')

# ---------------------
# API Views
# ---------------------

class RegisterView(generics.CreateAPIView):
    """API - Đăng ký người dùng"""
    serializer_class = RegisterSerializer


class LoginView(APIView):
    """API - Đăng nhập người dùng"""
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            login(request, serializer.validated_data)
            return Response({"message": "Login successful"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """API - Đăng xuất người dùng"""
    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"})


class LocationUpdateView(APIView):
    """API - Cập nhật vị trí hiện tại của người dùng"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LocationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Location updated"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationFetchView(APIView):
    """API - Lấy vị trí gần nhất của 1 người dùng theo tên"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            location = Location.objects.filter(user=user).latest('timestamp')
            serializer = LocationSerializer(location)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except Location.DoesNotExist:
            return Response({"error": "No location data found"}, status=404)


class AllUserLocationsView(APIView):
    """API - Lấy vị trí gần nhất của tất cả người dùng"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        locations = []
        users = User.objects.all()
        for user in users:
            latest = Location.objects.filter(user=user).order_by('-timestamp').first()
            if latest:
                locations.append(latest)
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)
