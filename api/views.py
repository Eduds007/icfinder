from rest_framework import generics

from icfinder_app.models import Projeto
from .serializers import ProjetoSerializer


class ProjetoList(generics.ListAPIView):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer

class ProjetoDetail(generics.RetrieveAPIView):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer