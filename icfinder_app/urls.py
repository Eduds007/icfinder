
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('register_professor/', views.ProfessorRegisterView.as_view(), name='register_professor')
]