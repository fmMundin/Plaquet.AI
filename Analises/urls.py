from django.urls import path
from . import views

app_name = 'Analises'  # Adicionar namespace para evitar conflitos

urlpatterns = [
    path('', views.analises, name='analises'),  # Esta é a view principal
    path('criar/', views.criar_analise, name='criar_analise'),
    path('deletar/<int:analise_id>/', views.deletar_analise, name='deletar_analise'),
    path('detalhes/<int:analise_id>/', views.detalhes_analise, name='detalhes_analise'),
    path('editar/<int:analise_id>/', views.editar_analise, name='editar_analise'),
]