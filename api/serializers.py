from rest_framework import serializers

from icfinder_app.models import Projeto

class ProjetoSerializer(serializers.ModelSerializer):
    lab = serializers.SerializerMethodField()
    responsavel = serializers.SerializerMethodField()

    def get_lab(self, projeto):
        return {
            'sigla': projeto.lab.sigla,
            'nomeCompleto': projeto.lab.nomeCompleto,
        }
    
    def get_responsavel(self, projeto):
        return {
            'nome': projeto.responsavel.user.first_name,
            'departamento': projeto.responsavel.departamento.departamento
        }

    class Meta:
        model = Projeto
        fields = ['id', 'responsavel', 'lab', 'titulo', 'descricao', 'about', 'vagas', 'bgImg', 'cardImg', 'date']