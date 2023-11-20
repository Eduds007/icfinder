
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('', views.Index.as_view(), name='index'),
    path('registration_student/', views.AlunoRegistrationView.as_view(), name='registration_student'),
    path('registration_professor/<int:professor_id>', views.ProfessorRegistrationView.as_view(), name='registration_professor'),
    path('send_token/', views.ProfessorTokenView.as_view(), name='send_token'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('project/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('chat/<int:receiver_id>/', views.chat, name='chat'),
    path('chats', views.chat_list, name='chats'),
]