from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Users
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

    # aceitar apenas emails no domínio usp
    #def clean_email(self):
    #    email = self.cleaned_data.get('email')
    #    if email and not email.endswith('@usp.br'):
    #        raise ValidationError("Insira seu email USP.")
    #    return email

