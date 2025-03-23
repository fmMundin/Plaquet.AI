from django.urls import path
from . import views

app_name = 'Analises'

urlpatterns = [
    path('', views.index, name='index'),
    path('analises/', views.analises, name='analises'),
    path('detalhes/<str:analise_id>/', views.detalhes_analise, name='detalhes_analise'),  # Mudado para str
    path('criar/', views.criar_analise, name='criar_analise'),
    path('deletar/<str:analise_id>/', views.deletar_analise, name='deletar_analise'),  # Mudado para str
    path('editar/<str:analise_id>/', views.editar_analise, name='editar_analise'),  # Mudado para str
]