from django.urls import path
from . import views

app_name = 'Analises'

urlpatterns = [
    path('', views.index, name='index'),                    # Página inicial (raiz)
    path('analises/', views.analises, name='analises'),     # Lista de análises
    path('detalhes/<int:analise_id>/', views.detalhes_analise, name='detalhes_analise'),
    path('criar/', views.criar_analise, name='criar_analise'),
    path('deletar/<int:analise_id>/', views.deletar_analise, name='deletar_analise'),
    path('editar/<int:analise_id>/', views.editar_analise, name='editar_analise'),
    path('analises/', include('Analises.urls')),
]
