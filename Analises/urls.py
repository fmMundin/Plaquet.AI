from django.urls import path
from . import views
from . import views_realtime
from . import views_about

app_name = 'Analises'

urlpatterns = [
    path('', views.index, name='index'),                    # Página inicial (raiz)
    path('analises/', views.analises, name='analises'),     # Lista de análises
    path('sobre/', views_about.about, name='about'),        # Página sobre
    path('detalhes/<int:analise_id>/', views.detalhes_analise, name='detalhes_analise'),
    path('criar/', views.criar_analise, name='criar_analise'),
    path('deletar/<int:analise_id>/', views.deletar_analise, name='deletar_analise'),
    path('editar/<int:analise_id>/', views.editar_analise, name='editar_analise'),
    
    # Rotas para análise em tempo real
    path('realtime/', views_realtime.realtime_analysis, name='realtime_analysis'),
    path('video-feed/', views_realtime.video_feed, name='video_feed'),
    path('stop-analysis/', views_realtime.stop_analysis, name='stop_analysis'),
    path('realtime/', views_realtime.realtime_analysis, name='realtime_analysis'),
    path('video-feed/', views_realtime.video_feed, name='video_feed'),
]
