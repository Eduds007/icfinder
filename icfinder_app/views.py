from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

def login(request):
    context = {}
    return render(request, 'icfinder_app/login.html', context)

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