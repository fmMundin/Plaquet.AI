from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('criar/', views.criar_analise, name='criar_analise'),
    path('deletar/<int:analise_id>/', views.deletar_analise, name='deletar_analise'),
]