from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'icfinder_app/index.html', context)