from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Users, Professor
import secrets
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    widgets = {
        'username': forms.TextInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Email usp'}),
        'password': forms.PasswordInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Senha' }),
    }

    username = forms.CharField(widget=widgets['username'])
    password = forms.CharField(widget=widgets['password'])

class StudentCreationForm(UserCreationForm):
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

class ProfessorValidationForm(forms.Form):
        email = forms.EmailField()
        token = forms.CharField()

class ProfessorAttributesForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['departamento', 'disponibilidade', 'lab']
        widgets = {
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'disponibilidade': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lab': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

class ProfessorRegisterForm(forms.ModelForm):
    email = forms.EmailField()  # Add the email field to the form

    class Meta:
        model = Professor
        fields = ['email']

    def generate_token(self):
        return secrets.token_hex(20)

    def save(self, commit=True):
        email = self.cleaned_data['email']

        # Create a new Users instance
        user_instance = Users.objects.create(email=email)

        # Create a new Professor instance
        instance = Professor(user=user_instance)
        instance.token = self.generate_token()
        instance.login_completed = False  # Set login_completed to False

        if commit:
            user_instance.save()
            instance.save()

        return instance