
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('', views.index, name='index'),
    path('registration_choice/', views.registration_choice, name='registration_choice'),
    path('registration_student/', views.AlunoRegistrationView.as_view(), name='registration_student'),
    path('validate_professor/', views.validate_professor, name='validate_professor'),
    path('registration_professor/<int:professor_id>', views.ProfessorRegistrationView.as_view(), name='registration_professor'),
    path('register_professor/', views.ProfessorRegisterView.as_view(), name='register_professor')
]