from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfessorRegisterForm
from django.views.generic.edit import CreateView
from .models import ProfessorRegister
from django.core.mail import EmailMessage


def login_view(request):
    if request.method == 'POST':
        login_form = CustomAuthenticationForm(request, request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return redirect('index')
    else:
        login_form = CustomAuthenticationForm()

    return render(
        request,
        'icfinder_app/login.html',
        {'login_form': login_form}
    )


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'icfinder_app/register.html', {'form': form})

def index(request):
    context = {}
    return render(request, 'icfinder_app/index.html', context)


class ProfessorRegisterView(CreateView):
    model = ProfessorRegister
    form_class = ProfessorRegisterForm
    template_name = 'register_professor.html'
    
    def get_success_url(self):
        return reverse('register_professor')

    def form_valid(self, form):
        response = super().form_valid(form)

        subject = 'Your Registration Token'
        body = f'Thank you for registering! Your token is: {form.instance.token}'
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