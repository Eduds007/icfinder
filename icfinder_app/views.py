from typing import Any
from django.views import generic, View
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from .forms import AlunoCreationForm, ProfessorCreationForm, ProfessorValidationForm, CustomAuthenticationForm, ProfessorTokenForm, MessageForm
from django.views.generic.edit import CreateView, FormView
from .models import Professor, Aluno, Users, Projeto, InscricaoProjeto, Conversation, Message
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
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('index')

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)

class RegistrationChoiceView(View):
    template_name = 'icfinder_app/registration_choice.html'

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, self.template_name)

class AlunoRegistrationView(FormView):    
    template_name = 'registration_student.html'
    form_class = AlunoCreationForm

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        password1 = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']

        if password1 != password2:
            form.add_error('password2', 'Senhas não correspondentes.')
            return self.form_invalid(form)

        user_instance = Users.objects.create(
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
            phone_number=form.cleaned_data['phone_number'],
            short_bio=form.cleaned_data['short_bio'],
        )

        aluno_instance = Aluno.objects.create(
            user=user_instance,
            curso=form.cleaned_data['curso'],
        )

        aluno_instance.interests.set(form.cleaned_data['interests'])

        # Atribui senha ao usuário
        password1 = form.cleaned_data['password1']
        user_instance.set_password(password1)
        user_instance.save()
        login(self.request, user_instance)

        return redirect('index')

class ValidateProfessorView(View):
    template_name = 'icfinder_app/validate_professor.html'
    form_class = ProfessorValidationForm

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            token = form.cleaned_data['token']

            professor = Professor.objects.filter(
                user__email=email,
                token=token,
                login_completed=False
            ).first()

            if professor:
                request.session['validated_email'] = email
                return redirect('registration_professor', professor_id=professor.id)
            else:
                form.add_error(None, "Email ou token inválido.")

        return render(request, self.template_name, {'form': form})

class ProfessorRegistrationView(FormView):
    template_name = 'registration_professor.html'
    form_class = ProfessorCreationForm

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        password1 = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']

        if password1 != password2:
            form.add_error('password2', 'Senhas não correspondentes.')
            return self.form_invalid(form)

        email_from_session = self.request.session.get('validated_email')
        user_instance = Users.objects.get(email=email_from_session)

        # Atualiza com os dados faltantes de usuário
        user_instance.first_name = form.cleaned_data['first_name']
        user_instance.last_name = form.cleaned_data['last_name']
        user_instance.phone_number = form.cleaned_data['phone_number']
        user_instance.short_bio = form.cleaned_data['short_bio']
        user_instance.save()

        # Atualiza os atributos agora com um professor com registro completo
        professor_instance = Professor.objects.get(user=user_instance)
        professor_instance.departamento = form.cleaned_data['departamento']
        professor_instance.disponibilidade = form.cleaned_data['disponibilidade']
        professor_instance.lab.set(form.cleaned_data['lab'])
        professor_instance.token = None
        professor_instance.login_completed = True
        professor_instance.save()

        # Atribui a senha ao usuário
        password1 = form.cleaned_data['password1']
        user_instance.set_password(password1)
        user_instance.save()
        login(self.request, user_instance)

        return redirect('index')

class Index(LoginRequiredMixin, FilterView):
    model = Projeto
    template_name = 'icfinder_app/index.html'
    filterset_class = ProjetoFilter
    context_object_name = 'projetos'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(Prefetch("inscritos", queryset=InscricaoProjeto.objects.filter(estado='pendente')))
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['num_projetos'] = self.get_queryset().filter(self.filterset_class(self.request.GET).qs.query.where).count()
        return context
    
class ProfessorTokenView(UserPassesTestMixin, CreateView):
    model = Professor
    form_class = ProfessorTokenForm
    template_name = 'send_token.html'
    
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')

    def get_success_url(self):
        return reverse('send_token')

    def form_valid(self, form):
        response = super().form_valid(form)

        subject = 'Token para iniciar cadastro no ICFinder'
        body = f'Para registrar sua conta no ICFinder e ter as permissões para gerenciar seus projetos, encontrando alunos para integrar os seus grupos de pesquisa, utilize o seu email usp e o token {self.object.token}.'
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


class ProjectDetailView(generic.DetailView):
    model = Projeto
    template_name = 'icfinder_app/detail.html'
    context_object_name = 'projeto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)# Adicionando variável ao contexto
        try:
            aluno =  Aluno.objects.get(user =self.request.user)
            context['inscricao_estado'] = self.get_inscricao_estado()
        except Aluno.DoesNotExist:
            context['inscricao_estado'] = ''
    
        
            
        context['inscritos'] = self.get_inscritos()
        print(context)
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
            print(user_email)
            user = Users.objects.filter(email = user_email).first()
            print(user)
            aluno = get_object_or_404(Aluno, user=user)
            inscricao, created = InscricaoProjeto.objects.get_or_create(aluno=aluno, projeto=projeto)
            inscricao.estado = 'aceito'
            inscricao.save()
            projeto.vagas -=1 
            projeto.save()


        elif action.startswith('recusar_'):
            user_id = action.split('_')[1]
            user = Users.objects.filter(id = user_id).first()
            aluno = get_object_or_404(Aluno, user=user)
            inscricao, created = InscricaoProjeto.objects.get_or_create(aluno=aluno, projeto=projeto)
            inscricao.estado = 'recusado'
            inscricao.save()


        return HttpResponseRedirect(reverse('detail', args=[str(projeto.id)]))


class ProjectCreateView(generic.CreateView):
    model = Projeto
    template_name = 'icfinder_app/new.html'
    success_url = reverse_lazy('index')
    fields = '__all__'


@login_required
def chat(request, receiver_id):
    receiver = get_object_or_404(Users, id=receiver_id)
    participants = [request.user, receiver]
    

    # Verifica se a conversa já existe entre os participantes
    conversation = Conversation.objects.filter(participants__in=participants).distinct()

    if not conversation.exists():
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()

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