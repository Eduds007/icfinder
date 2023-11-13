from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic


from .models import Projeto

class Index(generic.ListView):
    model = Projeto
    template_name = 'icfinder_app/index.html'
    context_object_name = 'projetos'
    
def login (request):
    context = {}
    return render(request, 'icfinder_app/login.html', context)