from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Users, ProfessorRegister
import secrets
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    widgets = {
        'username': forms.TextInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Email usp'}),
        'password': forms.PasswordInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Senha' }),
    }

    username = forms.CharField(widget=widgets['username'])
    password = forms.CharField(widget=widgets['password'])

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'interests', 'email', 'phone_number', 'short_bio']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'interests': 'Interesses',
            'email': 'Email',
            'phone_number': 'Celular',
            'short_bio': 'Short Bio',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your last name'}),
            'interests': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your interests'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your phone number'}),
            'short_bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a short bio'}),
        }

    # aceitar apenas emails no domínio usp
    #def clean_email(self):
    #    email = self.cleaned_data.get('email')
    #    if email and not email.endswith('@usp.br'):
    #        raise ValidationError("Insira seu email USP.")
    #    return email

class ProfessorRegisterForm(forms.ModelForm):
    class Meta:
        model = ProfessorRegister
        fields = ['email']

    def generate_token(self):
        return secrets.token_hex(20)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.token = self.generate_token()
        if commit:
            instance.save()
        return instance