from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Analise
from datetime import datetime
import os
import logging
from pathlib import Path
from scripts.infer import run_inference
import traceback
from django.db import transaction
from django.core.files import File
from django.conf import settings
from django.utils import timezone
from zoneinfo import ZoneInfo  # Para Python 3.9+
import shutil
import time
from scripts.analysis_service import analysis_service

logger = logging.getLogger(__name__)

def copiar_imagem_para_static(analise):
    """Copia as imagens da análise para a pasta static/images"""
    try:
        # Criar diretório se não existir
        static_img_dir = settings.BASE_DIR / 'static' / 'images'
        static_img_dir.mkdir(parents=True, exist_ok=True)

        # Copiar imagem original
        if analise.img:
            shutil.copy2(
                analise.img.path,
                static_img_dir / 'original.jpg'
            )

        # Copiar imagem com detecções
        if analise.img_resultado:
            shutil.copy2(
                analise.img_resultado.path,
                static_img_dir / 'detected.jpg'
            )
        return True
    except Exception as e:
        print(f"Erro ao copiar imagens: {e}")
        return False

# Create your views here.
def analises(request):
    """View para listar todas as análises"""
    try:
        analises = Analise.objects.all().order_by('-data_criacao')
        return render(request, 'Analises/analises.html', {'analises': analises})
    except Exception as e:
        logger.error(f"Erro ao listar análises: {str(e)}")
        messages.error(request, "Erro ao carregar análises")
        return render(request, 'Analises/analises.html', {'analises': []})

def criar_analise(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                if 'img' not in request.FILES:
                    return JsonResponse({'success': False, 'error': 'Imagem não enviada'})

                # Criar análise
                analise = Analise(
                    titulo=request.POST['titulo'],
                    paciente=request.POST['paciente'],
                    img=request.FILES['img'],
                    status='processando'
                )
                analise.save()

                # Processar imagem
                results = analysis_service.process_image(analise.img.path)

                if results['success']:
                    # Atualizar análise com resultados
                    analise.n_plaquetas = results['cell_counts'].get('plaqueta', 0)
                    analise.n_celulas_brancas = sum(
                        results['cell_counts'].get(tipo, 0) 
                        for tipo in ['leucocito', 'linfocito', 'monocito', 'basofilo', 
                                   'neutrofilo_banda', 'neutrofilo_segmentado', 'eosinofilo']
                    )
                    analise.n_celulas_vermelhas = results['cell_counts'].get('hemacia', 0)
                    analise.acuracia = results['accuracy'] * 100
                    analise.tempo_processamento = results['processing_time']
                    analise.status = 'concluido'
                    analise.save()

                    return JsonResponse({'success': True})
                else:
                    analise.status = 'erro'
                    analise.erro_msg = results.get('error', 'Erro desconhecido')
                    analise.save()
                    return JsonResponse({'success': False, 'error': results['error']})

        except Exception as e:
            logger.error(f"Erro ao processar análise: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método não permitido'})

def deletar_analise(request, analise_id):
    if request.method == 'POST':
        try:
            analise = get_object_or_404(Analise, pk=analise_id)
            titulo = analise.titulo  # Guardar o título antes de deletar
            analise.delete()
            return JsonResponse({
                'success': True,
                'message': f'Análise "{titulo}" excluída com sucesso!'
            })
        except Exception as e:
            logger.error(f"Erro ao excluir análise {analise_id}: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Erro ao excluir análise: {str(e)}'
            })
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

def detalhes_analise(request, analise_id):
    try:
        analise = get_object_or_404(Analise, pk=analise_id)
        return render(request, 'Analises/detalhes.html', {
            'analise': analise
        })
    except Exception as e:
        logger.error(f"Erro ao exibir detalhes da análise {analise_id}: {str(e)}", exc_info=True)
        messages.error(request, f'Erro ao exibir detalhes: {str(e)}')
        return redirect('Analises:analises')

def editar_analise(request, analise_id):
    if request.method == 'POST':
        try:
            analise = get_object_or_404(Analise, pk=analise_id)
            dados_antigos = f"Título: {analise.titulo}, Paciente: {analise.paciente}"
            
            # Atualizar dados
            analise.titulo = request.POST.get('titulo', analise.titulo)
            analise.paciente = request.POST.get('paciente', analise.paciente)
            
            # Registrar modificação
            alteracoes = f"Alteração nos dados (Anterior: {dados_antigos})"

            analise.registrar_modificacao(alteracoes)
            
            analise.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Análise atualizada com sucesso!',
                'ultima_modificacao': analise.ultima_modificacao.strftime('%d/%m/%Y %H:%M:%S'),
                'modificado_por': analise.modificado_por
            })
        except Exception as e:
            logger.error(f"Erro ao editar análise: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

def index(request):
    static_images_path = os.path.join(settings.BASE_DIR, 'static', 'images')
    images_exist = (
        os.path.exists(os.path.join(static_images_path, 'original.png')) and 
        os.path.exists(os.path.join(static_images_path, 'detected.png'))
    )
    
    return render(request, 'Analises/index.html', {
        'original_exists': images_exist
    })