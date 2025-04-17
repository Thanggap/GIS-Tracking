from django.db import models
from django.contrib.auth.models import AbstractUser

# -----------------------------------------
# Model người dùng kế thừa từ AbstractUser
# Thêm trường avatar để hiển thị marker
# -----------------------------------------
class User(AbstractUser):
    avatar = models.CharField(
        max_length=255,
        default='tracking/avatar/default.png'  # Ảnh mặc định nếu chưa chọn
    )

# -----------------------------------------
# Model lưu vị trí (lat, lng) người dùng
# Mỗi lần gửi sẽ lưu kèm thời gian timestamp
# -----------------------------------------
class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ({self.latitude}, {self.longitude})"
