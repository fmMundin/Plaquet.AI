from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Analise
from datetime import datetime

# Create your views here.
def index(request):
    analises = Analise.objects.all()
    return render(request, 'Analises/index.html', {'analises': analises})

def criar_analise(request):
    if request.method == 'POST':
        try:
            analise = Analise.objects.create(
                titulo=request.POST['titulo'],
                paciente=request.POST['paciente'],
                img=request.FILES['img'],
                data_analise=datetime.now()
            )
            messages.success(request, 'Análise iniciada com sucesso!')
            return redirect('index')
        except Exception as e:
            messages.error(request, f'Erro ao criar análise: {str(e)}')
            return redirect('index')
    return redirect('index')

def deletar_analise(request, analise_id):
    if request.method == 'POST':
        analise = get_object_or_404(Analise, pk=analise_id)
        try:
            # Deletar arquivo de imagem se existir
            if analise.img:
                analise.img.delete()
            if analise.img_resultado:
                analise.img_resultado.delete()
            analise.delete()
            messages.success(request, 'Análise excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir análise: {str(e)}')
    return redirect('index')