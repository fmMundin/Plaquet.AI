from django.urls import path
from . import views

app_name = 'Analises'

urlpatterns = [
    path('', views.index, name='index'),
    path('analises/', views.analises, name='analises'),
    path('analises/criar/', views.criar_analise, name='criar_analise'),
    path('analises/<int:analise_id>/detalhes/', views.detalhes_analise, name='detalhes_analise'),
    path('analises/<int:analise_id>/editar/', views.editar_analise, name='editar_analise'),
    path('analises/<int:analise_id>/deletar/', views.deletar_analise, name='deletar_analise'),
]