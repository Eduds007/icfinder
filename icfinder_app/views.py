from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from .forms import StudentCreationForm, ProfessorAttributesForm, ProfessorValidationForm, CustomAuthenticationForm, ProfessorRegisterForm
from django.views.generic.edit import CreateView
from .models import Professor
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


def registration_choice(request):
    return render(request, 'icfinder_app/registration_choice.html')

def registration_student(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = StudentCreationForm()
    return render(request, 'icfinder_app/registration_student.html', {'form': form})

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
                # Redirect to the professor_attributes view with the professor's ID
                return redirect('professor_attributes', professor_id=professor.id)
            else:
                # Handle invalid input, e.g., show an error message
                form.add_error(None, "Invalid email or token.")
    else:
        form = ProfessorValidationForm()

    return render(request, 'icfinder_app/validate_professor.html', {'form': form})

def professor_attributes(request, professor_id):
    professor = Professor.objects.get(id=professor_id)

    if request.method == 'POST':
        form = ProfessorAttributesForm(request.POST, instance=professor)
        if form.is_valid():
            # Save the attributes
            form.save()

            # Update the professor and set login_completed to True
            professor.login_completed = True
            professor.token = None
            professor.save()

            return redirect('index')  # Redirect to the desired page after saving the attributes
    else:
        form = ProfessorAttributesForm(instance=professor)

    # Disable the email field in the form
    #form.fields['user__email'].widget.attrs['disabled'] = True

    return render(request, 'icfinder_app/professor_attributes.html', {'form': form, 'professor': professor})

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