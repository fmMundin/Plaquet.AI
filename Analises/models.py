from django.db import models
from django.utils import timezone
import os

class Analise(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluido', 'Concluído'),
        ('erro', 'Erro')
    ]

    titulo = models.CharField(max_length=200)
    paciente = models.CharField(max_length=200)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_analise = models.DateTimeField(null=True, blank=True)
    img = models.ImageField(upload_to='analises/', null=True, blank=True)  # Modificado para permitir null
    img_resultado = models.ImageField(upload_to='resultados/', null=True, blank=True)
    n_plaquetas = models.IntegerField(null=True, blank=True)
    n_celulas_brancas = models.IntegerField(null=True, blank=True)
    n_celulas_vermelhas = models.IntegerField(null=True, blank=True)
    acuracia = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    erro_msg = models.TextField(null=True, blank=True)
    tempo_processamento = models.FloatField(null=True, blank=True)
    ultima_modificacao = models.DateTimeField(null=True, blank=True)
    modificado_por = models.CharField(max_length=100, null=True, blank=True)
    historico_modificacoes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Análise'
        verbose_name_plural = 'Análises'

    def __str__(self):
        return f"{self.titulo} - {self.paciente}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Salva a instância normalmente

    def delete(self, *args, **kwargs):
        # Deletar arquivos primeiro
        if self.img:
            self.img.delete()
        if self.img_resultado:
            self.img_resultado.delete()
        super().delete(*args, **kwargs)

    def registrar_modificacao(self, alteracoes, usuario="Sistema"):
        self.ultima_modificacao = timezone.now()
        self.modificado_por = usuario
        
        # Adicionar nova entrada ao histórico
        novo_registro = f"[{timezone.now().strftime('%d/%m/%Y %H:%M:%S')}] {usuario}: {alteracoes}\n"
        if self.historico_modificacoes:
            self.historico_modificacoes += novo_registro
        else:
            self.historico_modificacoes = novo_registro
