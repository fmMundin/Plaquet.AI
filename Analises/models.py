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

    TIPO_ANALISE_CHOICES = [
        ('imagem', 'Imagem Única'),
        ('tempo_real', 'Tempo Real'),
        ('video', 'Vídeo')
    ]

    titulo = models.CharField(max_length=200)
    data_criacao = models.DateTimeField(auto_now_add=True)
    paciente = models.CharField(max_length=200)
    tipo_analise = models.CharField(max_length=20, choices=TIPO_ANALISE_CHOICES, default='imagem')
    img = models.ImageField(upload_to='analises/', null=True, blank=True)
    img_resultado = models.ImageField(upload_to='resultados/', null=True, blank=True)
    video = models.FileField(upload_to='analises/videos/', null=True, blank=True)
    video_resultado = models.FileField(upload_to='resultados/videos/', null=True, blank=True)
    n_plaquetas = models.IntegerField(null=True, blank=True)
    n_celulas_brancas = models.IntegerField(null=True, blank=True)
    n_celulas_vermelhas = models.IntegerField(null=True, blank=True)
    n_linfocitos = models.IntegerField(null=True, blank=True)
    n_monocitos = models.IntegerField(null=True, blank=True)
    n_basofilos = models.IntegerField(null=True, blank=True)
    n_neutrofilos_banda = models.IntegerField(null=True, blank=True)
    n_neutrofilos_segmentados = models.IntegerField(null=True, blank=True)
    n_mielocitos = models.IntegerField(null=True, blank=True)
    n_metamielocitos = models.IntegerField(null=True, blank=True)
    n_promielocitos = models.IntegerField(null=True, blank=True)
    n_eosinofilos = models.IntegerField(null=True, blank=True)
    acuracia = models.FloatField(null=True, blank=True)
    data_analise = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    erro_msg = models.TextField(null=True, blank=True)
    tempo_processamento = models.FloatField(null=True, blank=True)
    esta_gravando = models.BooleanField(default=False)
    duracao_video = models.FloatField(null=True, blank=True)
    
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
        if not self.data_analise:
            self.data_analise = timezone.now()
        super(Analise, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Deletar arquivos associados
        if self.img and os.path.isfile(self.img.path):
            os.remove(self.img.path)
        if self.img_resultado and os.path.isfile(self.img_resultado.path):
            os.remove(self.img_resultado.path)
        if self.video and os.path.isfile(self.video.path):
            os.remove(self.video.path)
        if self.video_resultado and os.path.isfile(self.video_resultado.path):
            os.remove(self.video_resultado.path)
        super().delete(*args, **kwargs)


        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Deletar arquivos associados
        if self.img and os.path.isfile(self.img.path):
            os.remove(self.img.path)
        if self.img_resultado and os.path.isfile(self.img_resultado.path):
            os.remove(self.img_resultado.path)
        super().delete(*args, **kwargs)
    
    @property
    def total_plaquetas(self):
        # Soma das plaquetas de todas as imagens + plaquetas da análise principal
        total_imagens = sum(img.n_plaquetas or 0 for img in self.imagens_analise.all())
        return total_imagens + (self.n_plaquetas or 0)
    
    @property
    def total_celulas_brancas(self):
        total_imagens = sum(img.n_celulas_brancas or 0 for img in self.imagens_analise.all())
        return total_imagens + (self.n_celulas_brancas or 0)
    
    @property
    def total_celulas_vermelhas(self):
        total_imagens = sum(img.n_celulas_vermelhas or 0 for img in self.imagens_analise.all())
        return total_imagens + (self.n_celulas_vermelhas or 0)

class ImagemAnalise(models.Model):
    analise = models.ForeignKey(Analise, on_delete=models.CASCADE, related_name='imagens_analise')
    imagem = models.ImageField(upload_to='analises/')
    imagem_resultado = models.ImageField(upload_to='resultados/', null=True, blank=True)
    n_plaquetas = models.IntegerField(null=True, blank=True)
    n_celulas_brancas = models.IntegerField(null=True, blank=True)
    n_celulas_vermelhas = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Imagem da Análise'
        verbose_name_plural = 'Imagens das Análises'

    def __str__(self):
        return f"Imagem {self.id} - Análise {self.analise.titulo}"

    def delete(self, *args, **kwargs):
        if self.imagem and os.path.isfile(self.imagem.path):
            os.remove(self.imagem.path)
        if self.imagem_resultado and os.path.isfile(self.imagem_resultado.path):
            os.remove(self.imagem_resultado.path)
        super().delete(*args, **kwargs)
