from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Professor, Aluno, Interesse, Curso, Projeto
import secrets
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class CustomAuthenticationForm(AuthenticationForm):
    widgets = {
        'username': forms.TextInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Email usp'}),
        'password': forms.PasswordInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Senha' }),
    }

    username = forms.CharField(widget=widgets['username'])
    password = forms.CharField(widget=widgets['password'])

class AlunoPerfilForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
        required=False
    )
    last_name = forms.CharField(
        label='Sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'}),
        required=False
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Seu email com domínio usp'}),
        required=False
    )
    interests = forms.ModelMultipleChoiceField(
        label='Interesses',
        queryset=Interesse.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )
    phone_number = forms.CharField(
        label='Celular',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular para contato'})
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
    profile_pic = forms.URLField(
        label='Imagem de perfil',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insira a URL da imagem'}),
        required=False
    )

    class Meta:
        model = Aluno
        fields = ['first_name', 'last_name', 'email', 'interests', 'phone_number', 'short_bio', 'curso', 'profile_pic']

    # aceitar apenas emails no domínio usp
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not email.endswith('@usp.br'):
            raise ValidationError("Insira seu email USP.")
        return email

class ProfessorPerfilForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
        required=False
    )
    last_name = forms.CharField(
        label='Sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'}),
        required=False
    )
    phone_number = forms.CharField(
        label='Celular',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular de contato'})
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
    profile_pic = forms.URLField(
        label='Imagem de perfil',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insira a URL da imagem'}),
        required=False
    )


    class Meta:
        model = Professor
        fields = ['first_name', 'last_name', 'phone_number', 'short_bio', 'departamento', 'disponibilidade', 'lab', 'profile_pic', 'password1', 'password2']

class ProfessorTokenForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Professor
        fields = ['email']

    def generate_token(self, length=20):
        byte_length = (length + 1) // 2
        return secrets.token_hex(byte_length)

    def save(self, commit=True):
        email = self.cleaned_data['email']
        password = self.generate_token()
        user_instance = User.objects.create_user(email=email, password=password, username=email)
        instance = Professor(user=user_instance)
        instance.token = password
        instance.login_completed = False

        if commit:
            user_instance.save()
            instance.save()

        return instance

class ProjetoForm(forms.ModelForm):
    titulo = forms.CharField(
        label='Título',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do projeto'})
    )
    descricao = forms.CharField(
        label='Descrição',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Breve descrição'})
    )
    about = forms.CharField(
        label='Sobre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Projeto em mais detalhes'})
    )
    vagas = forms.CharField(
        label='Vagas disponíveis',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de vagas'})
    )
    bgImg = forms.URLField(
        label='Imagem de fundo',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insira a URL da imagem'}),
        required=False
    )
    cardImg = forms.URLField(
        label='Imagem do card',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insira a URL da imagem'}),
        required=False
    )

    class Meta:
        model = Projeto
        fields = ['titulo', 'descricao', 'about', 'vagas', 'lab', 'bgImg', 'cardImg']

class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Digite sua mensagem...'}))