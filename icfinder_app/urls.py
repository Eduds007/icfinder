
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('', views.Index.as_view(), name='index'),
    path('registration_choice/', views.registration_choice, name='registration_choice'),
    path('registration_student/', views.AlunoRegistrationView.as_view(), name='registration_student'),
    path('validate_professor/', views.validate_professor, name='validate_professor'),
    path('registration_professor/<int:professor_id>', views.ProfessorRegistrationView.as_view(), name='registration_professor'),
    path('send_token/', views.ProfessorTokenView.as_view(), name='send_token')
]