from django.db import models

class Analise(models.Model):
    titulo = models.CharField(max_length=200)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.titulo

# Create your models here.
