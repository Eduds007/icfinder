import django_filters
from .models import Projeto

class ProjetoFilter(django_filters.FilterSet):
    disponibilidade = django_filters.BooleanFilter(field_name='vagas', label='Disponibilidade', lookup_expr='gt')
    ordem = django_filters.OrderingFilter(
        choices=(
            ('-date', 'Mais Recentes'),
            ('date', 'Mais Antigos'),
        ),
        field_name='data',
        label='Ordenar por',
    )

    class Meta:
        model =  Projeto
        fields = []