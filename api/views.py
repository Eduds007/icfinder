from rest_framework import generics

from icfinder_app.models import Projeto
from .serializers import ProjetoSerializer


class ProjetoList(generics.ListCreateAPIView):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer

class ProjetoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer