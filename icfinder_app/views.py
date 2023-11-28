from typing import Any
from django.views import generic, View
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from .forms import AlunoPerfilForm, ProfessorPerfilForm, CustomAuthenticationForm, ProfessorTokenForm, MessageForm, ProjetoForm
from django.views.generic.edit import CreateView, FormView, UpdateView
from .models import Professor, Aluno, Projeto, InscricaoProjeto, Conversation, Message, Interesse
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Prefetch
from .filters import ProjetoFilter
from django_filters.views import FilterView
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
import secrets

class CustomLoginView(LoginView):
    template_name = 'icfinder_app/login.html'
    form_class = CustomAuthenticationForm

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()

        professor = Professor.objects.filter(
            user__email=user.email,
            login_completed=False
        ).first()

        if professor:
            self.request.session['validated_email'] = user.email
            return redirect('registration_professor', professor_id=professor.id)

        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('index')

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)

class AlunoRegistrationView(View):
    template_name = 'icfinder_app/registration.html'
    form_class = AlunoPerfilForm

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        
        form = self.form_class()
        context = {'form': form, 'registration_type': 'student'}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 != password2:
                form.add_error('password2', 'Senhas não correspondentes.')
            else:
                user_instance = User.objects.create(
                    username=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                )

                aluno_instance = Aluno.objects.create(
                    user=user_instance,
                    curso=form.cleaned_data['curso'],
                    phone_number=form.cleaned_data['phone_number'],
                    short_bio=form.cleaned_data['short_bio'],
                )

                #aluno_instance.interests.set(form.cleaned_data['interests'])
                aluno_instance.interests.set([])

                # Atribui senha ao usuário
                password1 = form.cleaned_data['password1']
                user_instance.set_password(password1)
                user_instance.save()
                login(request, user_instance)

                return redirect('interests_selection')

        context = {'form': form, 'registration_type': 'student'}
        return render(request, self.template_name, context)

class InterestsSelectionView(LoginRequiredMixin, View):
    template_name = 'icfinder_app/interests_selection.html'
    success_url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'interests': Interesse.objects.all()})

    def post(self, request, *args, **kwargs):
        aluno_instance = Aluno.objects.get(user=request.user)
        aluno_instance.interests.set(request.POST.getlist('interests'))
        return redirect(self.success_url)
    
class ProfessorRegistrationView(FormView):
    template_name = 'icfinder_app/registration.html'
    form_class = ProfessorPerfilForm

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration_type'] = 'professor_registration'
        return context

    def form_valid(self, form):
        password1 = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']

        if password1 != password2:
            form.add_error('password2', 'Senhas não correspondentes.')
            return self.form_invalid(form)

        email_from_session = self.request.session.get('validated_email')
        user_instance = User.objects.get(email=email_from_session)

        # Atualiza com os dados faltantes de usuário
        user_instance.first_name = form.cleaned_data['first_name']
        user_instance.last_name = form.cleaned_data['last_name']
        user_instance.save()

        # Atualiza os atributos agora com um professor com registro completo
        professor_instance = Professor.objects.get(user=user_instance)
        professor_instance.departamento = form.cleaned_data['departamento']
        professor_instance.disponibilidade = form.cleaned_data['disponibilidade']
        professor_instance.lab.set(form.cleaned_data['lab'])
        professor_instance.token = None
        professor_instance.login_completed = True
        professor_instance.phone_number = form.cleaned_data['phone_number']
        professor_instance.short_bio = form.cleaned_data['short_bio']
        professor_instance.save()

        # Atribui a senha ao usuário
        password1 = form.cleaned_data['password1']
        user_instance.set_password(password1)
        user_instance.save()
        login(self.request, user_instance)

        return redirect('index')
    
class PerfilDetailView(LoginRequiredMixin, View):
    template_name = 'icfinder_app/perfil_detail.html'
    
    def get(self, request, *args, **kwargs):
        try:
            aluno_instance = Aluno.objects.get(user=request.user)
            is_aluno = True
        except Aluno.DoesNotExist:
            is_aluno = False

        try:
            professor_instance = Professor.objects.get(user=request.user)
            is_professor = True
        except Professor.DoesNotExist:
            is_professor = False

        context = {
            'user': request.user,
            'is_aluno': is_aluno,
            'is_professor': is_professor,
            'aluno': aluno_instance if is_aluno else None,
            'professor': professor_instance if is_professor else None,
        }

        return render(request, self.template_name, context)
    

class AlunoUpdateView(LoginRequiredMixin, UpdateView):
    model = Aluno
    template_name = 'icfinder_app/perfil_update.html'
    form_class = AlunoPerfilForm

    def get_object(self, queryset=None):
        return Aluno.objects.get(user=self.request.user)
    
    def form_valid(self, form):
        aluno_instance = form.save(commit=False)
        aluno_instance.phone_number = form.cleaned_data['phone_number']
        aluno_instance.short_bio = form.cleaned_data['short_bio']
        aluno_instance.profile_pic = form.cleaned_data['profile_pic']
        aluno_instance.save()

        return redirect('perfil_detail', pk=self.request.user.id)

    def get_form_kwargs(self):
        kwargs = super(AlunoUpdateView, self).get_form_kwargs()
        aluno_instance = self.get_object()
        kwargs['instance'] = aluno_instance
        kwargs['initial'] = {
            'phone_number': aluno_instance.phone_number,
            'short_bio': aluno_instance.short_bio,
            'profile_pic': aluno_instance.profile_pic
        }
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_aluno'] = True
        context['is_professor'] = False
        return context

class ProfessorUpdateView(LoginRequiredMixin, UpdateView):
    model = Professor
    template_name = 'icfinder_app/perfil_update.html'  
    form_class = ProfessorPerfilForm

    def get_object(self, queryset=None):
        return Professor.objects.get(user=self.request.user)

    def form_valid(self, form):
        professor_instance = form.save(commit=False)
        professor_instance.phone_number = form.cleaned_data['phone_number']
        professor_instance.short_bio = form.cleaned_data['short_bio']
        professor_instance.profile_pic = form.cleaned_data['profile_pic']
        professor_instance.save()

        return redirect('perfil_detail', pk=self.request.user.id)

    def get_form_kwargs(self):
        kwargs = super(ProfessorUpdateView, self).get_form_kwargs()
        professor_instance = self.get_object()
        kwargs['instance'] = professor_instance
        kwargs['initial'] = {
            'phone_number': professor_instance.phone_number,
            'short_bio': professor_instance.short_bio,
            'profile_pic': professor_instance.profile_pic
        }
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_aluno'] = False
        context['is_professor'] = True
        return context

class Index(LoginRequiredMixin, FilterView):
    model = Projeto
    template_name = 'icfinder_app/index.html'
    filterset_class = ProjetoFilter
    context_object_name = 'projetos'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(Prefetch("inscritos", queryset=InscricaoProjeto.objects.filter(estado='pendente')))
        return queryset

    def get_context_data(self, **kwargs):
        try:
            aluno_instance = Aluno.objects.get(user=self.request.user)
            is_aluno = True
        except Aluno.DoesNotExist:
            is_aluno = False

        try:
            professor_instance = Professor.objects.get(user=self.request.user)
            is_professor = True
        except Professor.DoesNotExist:
            is_professor = False

        context = super().get_context_data(**kwargs)
        context['is_aluno'] = is_aluno
        context['is_professor'] = is_professor
        context['num_projetos'] = self.get_queryset().filter(self.filterset_class(self.request.GET).qs.query.where).count()
        return context
    
class ProfessorTokenView(UserPassesTestMixin, CreateView):
    model = Professor
    form_class = ProfessorTokenForm
    template_name = 'icfinder_app/send_token.html'
    
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')

    def get_success_url(self):
        return reverse('send_token')

    def form_valid(self, form):
        response = super().form_valid(form)

        subject = 'Token para iniciar cadastro no ICFinder'
        body = f'Para registrar sua conta no ICFinder e ter as permissões para gerenciar seus projetos, encontrando alunos para integrar os seus grupos de pesquisa, utilize o seu email usp e o token {self.object.token} como senha para prosseguir no cadastro.'
        sender = 'noreply@semycolon.com'
        recipient = [form.cleaned_data['email']]

        email = EmailMessage(
            subject,
            body,
            sender,
            recipient
        )
        email.send(fail_silently=False)

        return response

class ResetPasswordView(FormView):
    template_name = 'icfinder_app/reset_password.html'
 
    def generate_token(self, length=15):
        byte_length = (length + 1) // 2
        return secrets.token_hex(byte_length)
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', '')
        if email:
            temp_password = self.generate_token()

            try:
                user_instance = User.objects.get(email=email)
                user_instance.set_password(temp_password)
                user_instance.save()

                subject = 'Token para redefinição de senha no ICFinder'
                body = f'Para recuperar sua conta no ICFinder, execute login com a senha temporária gerada e defina uma nova senha no seu perfil de usuário. A senha gerada é {temp_password}'
                sender = 'noreply@semycolon.com'
                recipient = [email]

                email_msg = EmailMessage(
                    subject,
                    body,
                    sender,
                    recipient
                )
                email_msg.send(fail_silently=False)

                return redirect(reverse('login'))
            except User.DoesNotExist:
                pass

        return render(request, self.template_name, {'error': 'Invalid email'})

class ProjectDetailView(generic.DetailView):
    model = Projeto
    template_name = 'icfinder_app/detail.html'
    context_object_name = 'projeto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)# Adicionando variável ao contexto
        try:
            aluno =  Aluno.objects.get(user=self.request.user)
            context['inscricao_estado'] = self.get_inscricao_estado()
        except Aluno.DoesNotExist:
            context['inscricao_estado'] = ''
    
        try:
            aluno_instance = Aluno.objects.get(user=self.request.user)
            is_aluno = True
        except Aluno.DoesNotExist:
            is_aluno = False

        try:
            professor_instance = Professor.objects.get(user=self.request.user)
            is_professor = True
        except Professor.DoesNotExist:
            is_professor = False
        
        context['is_aluno'] = is_aluno
        context['is_professor'] = is_professor
        context['professr'] = professor_instance if is_professor else None
        context['inscritos'] = self.get_inscritos()
        return context
    
    def get_inscritos(self):
        projeto = self.get_object()
        print(projeto)
        inscritos = InscricaoProjeto.objects.filter(projeto=projeto, estado='pendente')
        return inscritos
    
    def get_inscricao_estado(self):
        # Retorna o estado da inscrição do aluno no projeto atual
        aluno = get_object_or_404(Aluno, user=self.request.user)
        projeto = self.get_object()
        inscricao_projeto = InscricaoProjeto.objects.filter(aluno=aluno, projeto=projeto).first()
        return inscricao_projeto.estado if inscricao_projeto else None

    def post(self, request, *args, **kwargs):
        projeto = self.get_object()
        action = request.POST.get('action')

        if action == 'inscrever':

            aluno = get_object_or_404(Aluno, user=self.request.user)
            inscricao, created = InscricaoProjeto.objects.get_or_create(aluno=aluno, projeto=projeto)
            inscricao.estado = 'pendente'
            inscricao.save()
         
        elif action.startswith('aceitar_'):
            user_email = action.split('_')[1]
            user = User.objects.filter(email = user_email).first()
            aluno = get_object_or_404(Aluno, user=user)
            inscricao, created = InscricaoProjeto.objects.get_or_create(aluno=aluno, projeto=projeto)
            inscricao.estado = 'aceito'
            inscricao.save()
            projeto.vagas -=1 
            projeto.save()


        elif action.startswith('recusar_'):
            user_email = action.split('_')[1]
            user = User.objects.filter(email = user_email).first()
            aluno = get_object_or_404(Aluno, user=user)
            inscricao, created = InscricaoProjeto.objects.get_or_create(aluno=aluno, projeto=projeto)
            inscricao.estado = 'recusado'
            inscricao.save()


        return HttpResponseRedirect(reverse('detail', args=[str(projeto.id)]))


class ProjectUpdateView(generic.UpdateView):
    model = Projeto
    template_name = 'icfinder_app/update.html'
    form_class = ProjetoForm

    def form_valid(self, form):
        projeto_instance = self.object
        projeto_instance.lab=form.cleaned_data['lab']
        projeto_instance.titulo=form.cleaned_data['titulo']
        projeto_instance.descricao=form.cleaned_data['descricao']
        projeto_instance.about=form.cleaned_data['about']
        projeto_instance.vagas=form.cleaned_data['vagas']
        projeto_instance.bgImg=form.cleaned_data['bgImg']
        projeto_instance.cardImg=form.cleaned_data['cardImg']
        projeto_instance.save()

        return redirect('detail', pk=self.object.pk)

    def get_form_kwargs(self):
        kwargs = super(ProjectUpdateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'titulo': self.object.titulo,
            'descricao': self.object.descricao,
            'about': self.object.descricao
        }
        return kwargs
    

class ProjectCreateView(generic.CreateView):
    model = Projeto
    template_name = 'icfinder_app/new.html'
    success_url = reverse_lazy('index')
    form_class = ProjetoForm

    def form_valid(self, form):
        Projeto.objects.create(
                    responsavel=Professor.objects.get(user=self.request.user),
                    lab=form.cleaned_data['lab'],
                    titulo=form.cleaned_data['titulo'],
                    descricao=form.cleaned_data['descricao'],
                    about=form.cleaned_data['about'],
                    vagas=form.cleaned_data['vagas'],
                    bgImg=form.cleaned_data['bgImg'],
                    cardImg=form.cleaned_data['cardImg'],
                )

        return redirect('index')

class ProjectDeleteView(generic.DeleteView):
    model = Projeto
    template_name = 'icfinder_app/delete.html'
    success_url = reverse_lazy('index')


@login_required
def chat(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    participants = [f'{request.user.id}'+f'{receiver.id}',f'{receiver.id}'+f'{request.user.id}']
    
    # Verifica se a conversa já existe entre os participantes
    conversation = Conversation.objects.filter(conversation_id__in=participants).distinct()

    if not conversation.exists():
        conversation = Conversation.objects.create()
        conversation.participants.set([request.user.id,receiver.id ])
        conversation.conversation_id = f'{request.user.id}'+f'{receiver.id}'
        conversation.save()
        conversation = Conversation.objects.filter(conversation_id__in=participants).distinct()

    messages = Message.objects.filter(conversation=conversation[0]).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            print(content)
            Message.objects.create(conversation=conversation[0], sender=request.user, content=content)
            return redirect('chat', receiver_id=receiver.id)
    else:
        form = MessageForm()

    context = { 'receiver': receiver, 'messages': messages, 'conversation': conversation, 'form': form}
    
        
    return render(request, 'icfinder_app/chat.html', context=context)

def chat_list(request):
    chats = Conversation.objects.filter(participants=request.user)
 

    return render(request, 'icfinder_app/chats.html', {'chats':chats})