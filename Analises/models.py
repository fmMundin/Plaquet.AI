from django.db import models
from django.utils import timezone
from zoneinfo import ZoneInfo
import os

class Analise(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluido', 'Concluído'),
        ('erro', 'Erro')
    ]

    titulo = models.CharField(max_length=200)
    data_criacao = models.DateTimeField(auto_now_add=True)
    paciente = models.CharField(max_length=200)
    img = models.ImageField(upload_to='analises/', null=True, blank=True)
    img_resultado = models.ImageField(upload_to='resultados/', null=True, blank=True)
    n_plaquetas = models.IntegerField(null=True, blank=True)
    n_celulas_brancas = models.IntegerField(null=True, blank=True)
    n_celulas_vermelhas = models.IntegerField(null=True, blank=True)
    acuracia = models.FloatField(null=True, blank=True)
    data_analise = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    erro_msg = models.TextField(null=True, blank=True)
    tempo_processamento = models.FloatField(null=True, blank=True)
    
    # Campos para análise detalhada
    detalhes_processamento = models.JSONField(null=True, blank=True)
    confianca_deteccao = models.FloatField(null=True, blank=True)
    metadados_modelo = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Análise'
        verbose_name_plural = 'Análises'

    def __str__(self):
        return f"{self.titulo} - {self.paciente}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Deletar arquivos associados
        if self.img and os.path.isfile(self.img.path):
            os.remove(self.img.path)
        if self.img_resultado and os.path.isfile(self.img_resultado.path):
            os.remove(self.img_resultado.path)
        super().delete(*args, **kwargs)
