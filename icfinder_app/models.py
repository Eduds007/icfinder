from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.conf import settings

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

class Lab(models.Model):
    sigla = models.CharField(max_length=10)
    nomeCompleto = models.CharField(max_length=255)


    def __str__(self):
        return f'{self.nomeCompleto} ({self.sigla})'

class BaseModel(models.Model):
    phone_number = models.CharField(max_length=15, null=True)
    short_bio = models.CharField(max_length=225, null=True)
    profile_pic = models.URLField(null=True)

    class Meta:
        abstract = True

class Professor(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE)
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
    descricao = models.CharField(max_length=1000)
    about = models.CharField(max_length=1000)
    vagas = models.IntegerField(default=1)
    bgImg = models.URLField()
    cardImg = models.URLField()
    date = models.DateField(default=timezone.now)


    def __str__(self):
        return self.titulo

class Aluno(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE)
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
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    conversation_id = models.CharField(max_length=3)

    def __str__(self):
        participants_list =  self.participants.all()
        return f'Conversa com: {participants_list}'


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.conversation.id} at {self.timestamp}"

