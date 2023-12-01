import django_filters
from .models import Projeto

class ProjetoFilter(django_filters.FilterSet):
    disponibilidade = django_filters.BooleanFilter(field_name='vagas', label='Disponibilidade', method='filter_disponibilidade',)
    ordem = django_filters.OrderingFilter(
        choices=(
            ('-date', 'Mais Recentes'),
            ('date', 'Mais Antigos'),
        ),
        field_name='data',
        label='Ordenar por',
    )

    def filter_disponibilidade(self, queryset, name, value):
        if value:
            # If True, filter projects with vagas greater than 0
            return queryset.filter(vagas__gt=0)
        else:
            # If False, filter projects with vagas less than or equal to 0
            return queryset.filter(vagas__lte=0)

    class Meta:
        model =  Projeto
        fields = []