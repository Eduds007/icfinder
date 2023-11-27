from rest_framework import serializers

from icfinder_app.models import Projeto

class ProjetoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Projeto
        fields = ['responsavel', 'lab', 'titulo', 'descricao', 'about', 'vagas', 'bgImg', 'cardImg', 'date']