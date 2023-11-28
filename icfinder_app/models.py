from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.dispatch import receiver
from django.db.models.signals import post_save

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Interesse(models.Model):
    interesse = models.CharField(max_length=100)


    def __str__(self):
        return self.interesse

class Curso(models.Model):
    curso = models.CharField(max_length=100)


    def __str__(self):
        return self.curso

class Departamento(models.Model):
    departamento = models.CharField(max_length=100)


    def __str__(self):
        return self.departamento

class Users(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True)
    short_bio = models.CharField(max_length=225, null=True)
    is_admin = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class Lab(models.Model):
    sigla = models.CharField(max_length=10)
    nomeCompleto = models.CharField(max_length=255)


    def __str__(self):
        return f'{self.nomeCompleto} ({self.sigla})'

class Professor(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    departamento = models.ForeignKey(Departamento, null=True, on_delete=models.CASCADE)
    disponibilidade = models.BooleanField(default=True)
    lab = models.ManyToManyField(Lab)
    token = models.CharField(max_length=255, null=True)
    login_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} (Login não concluído)" if self.user and not self.login_completed else f"{self.user.email}"



class Projeto(models.Model):
    responsavel = models.ForeignKey(Professor, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=64)
    descricao = models.CharField(max_length=255)
    about = models.CharField(max_length=255 )
    vagas = models.IntegerField(default=1)
    bgImg = models.URLField()
    cardImg = models.URLField()
    date = models.DateField()


    def __str__(self):
        return self.titulo

class Aluno(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    interests = models.ManyToManyField(Interesse, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    projeto = models.ManyToManyField(Projeto, blank=True)


    def __str__(self):
        return self.user.email

class InscricaoProjeto(models.Model):
    ESTADO_CHOICES = (
        ('não aceito', 'Não Aceito'),
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
    )

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='inscritos')
    data_inscricao = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendente')


    def __str__(self):
        return self.aluno.user.email

@receiver(post_save, sender=InscricaoProjeto)
def register_project(sender, instance, **kwargs):
    if instance.estado == 'aceito':
        instance.aluno.projeto.add(instance.projeto)


class Conversation(models.Model):
    participants = models.ManyToManyField(Users, related_name='conversations')
    conversation_id = models.CharField(max_length=3)

    def __str__(self):
        participants_list =  self.participants.all()
        return f'Conversa com: {participants_list}'


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} in {self.conversation.id} at {self.timestamp}"

