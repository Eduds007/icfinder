from django.urls import path
from .views import ProjetoList, ProjetoDetail

urlpatterns = [
    path('project/<int:pk>/', ProjetoDetail.as_view()),
    path('project/', ProjetoList.as_view()),
]