
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.index, name='index'),
    path('registration_choice/', views.registration_choice, name='registration_choice'),
    path('registration_student/', views.registration_student, name='registration_student'),
    path('validate_professor/', views.validate_professor, name='validate_professor'),
    path('professor_attributes/<int:professor_id>', views.professor_attributes, name='professor_attributes'),
    path('register_professor/', views.ProfessorRegisterView.as_view(), name='register_professor')
]