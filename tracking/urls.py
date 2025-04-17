from django.urls import path
from .views import (
    # HTML views
    home_view, login_view, register_view, logout_view,
    map_view, profile_view, update_profile_view, change_password_view,

    # API views
    RegisterView, LoginView, LogoutView,
    LocationUpdateView, LocationFetchView, AllUserLocationsView
)

urlpatterns = [
    # -------------------------
    # GIAO DIỆN NGƯỜI DÙNG (HTML)
    # -------------------------

    path('', home_view, name='home'),  # Trang chủ
    path('login/', login_view, name='login'),  # Đăng nhập
    path('register/', register_view, name='register'),  # Đăng ký
    path('logout/', logout_view, name='logout'),  # Đăng xuất

    path('map/', map_view, name='map'),  # Bản đồ realtime
    path('profile/', profile_view, name='profile'),  # Trang hồ sơ cá nhân
    path('update-profile/', update_profile_view, name='update_profile'),  # Cập nhật tên/email
    path('change-password/', change_password_view, name='change_password'),  # Đổi mật khẩu

    # -------------------------
    # API ENDPOINTS (RESTful)
    # -------------------------

    path('api/register/', RegisterView.as_view(), name='api-register'),  # API Đăng ký
    path('api/login/', LoginView.as_view(), name='api-login'),  # API Đăng nhập
    path('api/logout/', LogoutView.as_view(), name='api-logout'),  # API Đăng xuất

    path('api/update_location/', LocationUpdateView.as_view(), name='api-update-location'),  # Cập nhật vị trí
    path('api/get_user_location/<str:username>/', LocationFetchView.as_view(), name='api-user-location'),  # Lấy vị trí 1 user
    path('api/get_all_locations/', AllUserLocationsView.as_view(), name='api-all-locations'),  # Lấy toàn bộ vị trí mới nhất
]
