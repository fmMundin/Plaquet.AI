from django.contrib import admin
from .models import Analise

@admin.register(Analise)
class AnaliseAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'paciente', 'n_plaquetas', 'acuracia', 'data_criacao')
    list_filter = ('data_criacao', 'paciente')
    search_fields = ('titulo', 'paciente')
    date_hierarchy = 'data_criacao'