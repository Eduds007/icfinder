
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('reset_password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('', views.Index.as_view(), name='index'),
    path('registration_student/', views.AlunoRegistrationView.as_view(), name='registration_student'),
    path('interests_selection/', views.InterestsSelectionView.as_view(), name='interests_selection'),
    path('registration_professor/<int:professor_id>', views.ProfessorRegistrationView.as_view(), name='registration_professor'),
    path('send_token/', views.ProfessorTokenView.as_view(), name='send_token'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('project/<int:pk>/update', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('project/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('perfil/<int:pk>/', views.PerfilDetailView.as_view(), name='perfil_detail'),
    path('perfil/<int:pk>/update/aluno/', views.AlunoUpdateView.as_view(), name='perfil_aluno_update'),
    path('perfil/<int:pk>/update/professor/', views.ProfessorUpdateView.as_view(), name='perfil_professor_update'),
    path('chat/<int:receiver_id>/', views.chat, name='chat'),
    path('chats', views.chat_list, name='chats'),
]