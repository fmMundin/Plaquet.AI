from django.db import models

class Analise(models.Model):
    titulo = models.CharField(max_length=200)
    data_criacao = models.DateTimeField(auto_now_add=True)
    paciente = models.CharField(max_length=200)
    img = models.ImageField(upload_to='analises/', null=True, blank=True)
    img_resultado = models.ImageField(upload_to='resultados/', null=True, blank=True)
    n_plaquetas = models.IntegerField(null=True, blank=True)
    acuracia = models.FloatField(null=True, blank=True)
    tempo_analise = models.FloatField(null=True, blank=True)
    data_analise = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Análise'
        verbose_name_plural = 'Análises'

    def __str__(self):
        return f"{self.titulo} - {self.paciente}"

# Create your models here.
