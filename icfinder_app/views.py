from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout
from .forms import AlunoCreationForm, ProfessorCreationForm, ProfessorValidationForm, CustomAuthenticationForm, ProfessorRegisterForm
from django.views.generic.edit import CreateView, FormView
from .models import Professor, Aluno, Users
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.conf import settings

def custom_logout(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

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


def registration_choice(request):
    return render(request, 'icfinder_app/registration_choice.html')

class AlunoRegistrationView(FormView):
    template_name = 'registration_student.html'
    form_class = AlunoCreationForm

    def form_valid(self, form):
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

        # Set the password for the user
        password1 = form.cleaned_data['password1']
        user_instance.set_password(password1)
        user_instance.save()

        # Log the user in
        login(self.request, user_instance)

        # Redirect to the success URL
        return redirect('index')

def validate_professor(request):
    if request.method == 'POST':
        form = ProfessorValidationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            token = form.cleaned_data['token']

            # Check for a matching professor with login_completed=False and the provided token
            professor = Professor.objects.filter(
                user__email=email,
                token=token,
                login_completed=False
            ).first()

            if professor:
                request.session['validated_email'] = email
                return redirect('registration_professor', professor_id=professor.id)
            else:
                # Handle invalid input, e.g., show an error message
                form.add_error(None, "Invalid email or token.")
    else:
        form = ProfessorValidationForm()

    return render(request, 'icfinder_app/validate_professor.html', {'form': form})

class ProfessorRegistrationView(FormView):
    template_name = 'registration_professor.html'
    form_class = ProfessorCreationForm

    def form_valid(self, form):
        # Retrieve email from the session
        email_from_session = self.request.session.get('validated_email')

        # Retrieve the existing Users instance
        user_instance = Users.objects.get(email=email_from_session)

        # Update the attributes of the Users instance
        user_instance.first_name = form.cleaned_data['first_name']
        user_instance.last_name = form.cleaned_data['last_name']
        user_instance.phone_number = form.cleaned_data['phone_number']
        user_instance.short_bio = form.cleaned_data['short_bio']
        user_instance.save()

        # Retrieve the existing Professor instance
        professor_instance = Professor.objects.get(user=user_instance)

        # Update the attributes of the Professor instance
        professor_instance.departamento = form.cleaned_data['departamento']
        professor_instance.disponibilidade = form.cleaned_data['disponibilidade']
        professor_instance.lab.set(form.cleaned_data['lab'])
        professor_instance.token = None
        professor_instance.login_completed = True
        professor_instance.save()

        # Set the password for the user
        password1 = form.cleaned_data['password1']
        user_instance.set_password(password1)
        user_instance.save()

        # Log the user in
        login(self.request, user_instance)

        # Redirect to the success URL
        return redirect('index')

@login_required
def index(request):
    context = {}
    return render(request, 'icfinder_app/index.html', context)


class ProfessorRegisterView(CreateView):
    model = Professor
    form_class = ProfessorRegisterForm
    template_name = 'register_professor.html'
    
    def get_success_url(self):
        return reverse('register_professor')

    def form_valid(self, form):
        response = super().form_valid(form)

        subject = 'Your Registration Token'
        body = f'Thank you for registering! Your token is: {self.object.token}'
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