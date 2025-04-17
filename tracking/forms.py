from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

# ---------------------------------------------------------
# Form cập nhật thông tin người dùng (username, email)
# Được dùng trong giao diện cập nhật hồ sơ cá nhân (update_profile)
# ---------------------------------------------------------
class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
