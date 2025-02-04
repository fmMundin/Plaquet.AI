from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Landing page
    path('analises/', views.analises, name='analises'),  # Página de análises
    path('criar/', views.criar_analise, name='criar_analise'),
    path('deletar/<int:analise_id>/', views.deletar_analise, name='deletar_analise'),
    path('detalhes/<int:analise_id>/', views.detalhes_analise, name='detalhes_analise'),
]