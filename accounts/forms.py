import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import User

EGYPT_PHONE_RE = re.compile(r"^(?:\+20|0020|0)?1[0125][0-9]{8}$")

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "mobile", "profile_picture"]

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"].replace(" ", "").replace("-", "")
        if not EGYPT_PHONE_RE.fullmatch(mobile):
            raise forms.ValidationError("Enter a valid Egyptian mobile number.")
        return mobile

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "mobile", "profile_picture", "birthdate", "facebook_profile", "country"]
        widgets = {"birthdate": forms.DateInput(attrs={"type": "date"})}

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"].replace(" ", "").replace("-", "")
        if not EGYPT_PHONE_RE.fullmatch(mobile):
            raise forms.ValidationError("Enter a valid Egyptian mobile number.")
        return mobile
