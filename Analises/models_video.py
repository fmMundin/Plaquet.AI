from django.db import models
from .models import Analise

class AnaliseVideo(Analise):
    TIPO_FONTE_CHOICES = [
        ('camera', 'Câmera'),
        ('arquivo', 'Arquivo de Vídeo')
    ]
    
    tipo_fonte = models.CharField(max_length=10, choices=TIPO_FONTE_CHOICES, default='camera')
    video_fonte = models.FileField(upload_to='analises/videos/fonte/', null=True, blank=True)
    video_resultado = models.FileField(upload_to='analises/videos/resultado/', null=True, blank=True)
    esta_gravando = models.BooleanField(default=False)
    duracao = models.FloatField(null=True, blank=True)  # Duração em segundos
    media_fps = models.FloatField(null=True, blank=True)  # Média de frames por segundo
    total_frames = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Análise em Vídeo'
        verbose_name_plural = 'Análises em Vídeo'
