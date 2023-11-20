from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Users, Professor, Aluno, Interesse, Curso
import secrets
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    widgets = {
        'username': forms.TextInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Email usp'}),
        'password': forms.PasswordInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Senha' }),
    }

    username = forms.CharField(widget=widgets['username'])
    password = forms.CharField(widget=widgets['password'])

class RegistrationChoiceForm(forms.Form):
    CHOICES = [
        ('student', 'Cadastrar como estudante'),
        ('professor', 'Cadastrar como professor'),
    ]

    registration_type = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='',
    )

class AlunoCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insira seu nome'})
    )
    last_name = forms.CharField(
        label='Sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insira seu sobrenome'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Seu email'})
    )
    interests = forms.ModelMultipleChoiceField(
        label='Interesses',
        queryset=Interesse.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        label='Celular',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your phone number'})
    )
    short_bio = forms.CharField(
        label='Short Bio',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escreva uma breve descrição sobre você'})
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'})
    )
    password2 = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme a senha'})
    )

    curso = forms.ModelChoiceField(
        label='Curso',
        queryset=Curso.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Aluno
        fields = ['first_name', 'last_name', 'email', 'interests', 'phone_number', 'short_bio', 'curso']

    # aceitar apenas emails no domínio usp
    #def clean_email(self):
    #    email = self.cleaned_data.get('email')
    #    if email and not email.endswith('@usp.br'):
    #        raise ValidationError("Insira seu email USP.")
    #    return email

class ProfessorValidationForm(forms.Form):
        email = forms.EmailField()
        token = forms.CharField()

class ProfessorCreationForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = forms.CharField()
    short_bio = forms.CharField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Professor
        fields = ['first_name', 'last_name', 'phone_number', 'short_bio', 'departamento', 'disponibilidade', 'lab', 'password1', 'password2']

class ProfessorTokenForm(forms.ModelForm):
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

class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Type your message...'}))