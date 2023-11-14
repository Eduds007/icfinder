from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Users

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'interests', 'email', 'phone_number', 'short_bio']

