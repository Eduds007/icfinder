from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import Users, Professor, Aluno, Interesse, Curso, Lab, Departamento
import secrets
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    widgets = {
        'username': forms.TextInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Email usp'}),
        'password': forms.PasswordInput(attrs={'style': 'font-size: 20px; background: transparent; border: none; outline: none; color: black;', 'placeholder': 'Senha' }),
    }

    username = forms.CharField(widget=widgets['username'])
    password = forms.CharField(widget=widgets['password'])

class AlunoCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'})
    )
    last_name = forms.CharField(
        label='Sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Seu email com domínio usp'})
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

    class Meta:
        model = Aluno
        fields = ['first_name', 'last_name', 'email', 'interests', 'phone_number', 'short_bio', 'curso']

    # aceitar apenas emails no domínio usp
    #def clean_email(self):
    #    email = self.cleaned_data.get('email')
    #    if email and not email.endswith('@usp.br'):
    #        raise ValidationError("Insira seu email USP.")
    #    return email

class ProfessorCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'})
    )
    last_name = forms.CharField(
        label='Sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'})
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

    class Meta:
        model = Professor
        fields = ['first_name', 'last_name', 'phone_number', 'short_bio', 'departamento', 'disponibilidade', 'lab', 'password1', 'password2']

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


        user_instance = Users.objects.create(email=email)
        instance = Professor(user=user_instance)
        instance.token = self.generate_token()
        instance.login_completed = False
        user_instance.set_password(instance.token)

        if commit:
            user_instance.save()
            instance.save()

        return instance

class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Type your message...'}))



class PerfilEditForm(forms.ModelForm):
    # Campos específicos do Aluno
    interests = forms.ModelMultipleChoiceField(
        label='Interesses',
        queryset=Interesse.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required = False
    )
    curso = forms.ModelChoiceField(
        label='Curso',
        queryset=Curso.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required = False
    )

    # Campos específicos do Professor
    departamento = forms.ModelChoiceField(
        label='Departamento',
        queryset=Departamento.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required = False
    )
    disponibilidade = forms.BooleanField(
        label='Disponibilidade',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required = False
    )
    lab = forms.ModelMultipleChoiceField(
        label='Laboratórios',
        queryset=Lab.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required = False
    )

    class Meta:
        model = Users
        fields = ['phone_number', 'short_bio', 'interests', 'curso', 'departamento', 'disponibilidade','lab']

