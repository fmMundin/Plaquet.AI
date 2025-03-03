from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Analise
from datetime import datetime
import os
import logging
from pathlib import Path
from scripts.infer import process_image  # Mudamos para process_image
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
                # Validar imagem
                if 'img' not in request.FILES:
                    return JsonResponse({'success': False, 'error': 'Nenhuma imagem foi enviada'})
                
                img_file = request.FILES['img']
                if not img_file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    return JsonResponse({
                        'success': False, 
                        'error': 'Formato de imagem inválido. Use JPG, JPEG ou PNG'
                    })

                # Criar análise
                analise = Analise(
                    titulo=request.POST['titulo'],
                    paciente=request.POST['paciente'],
                    img=img_file,
                    status='processando',
                    data_analise=timezone.now()
                )
                analise.save()

                try:
                    # Configurar caminhos
                    weights_path = str(settings.BASE_DIR / 'scripts' / 'best.pt')
                    output_dir = str(settings.MEDIA_ROOT / 'resultados')

                    # Processar imagem
                    results = process_image(weights_path, str(analise.img.path), output_dir)
                    
                    if results['success']:
                        # Salvar imagem processada
                        processed_path = Path(results['output_path'])
                        if processed_path.exists():
                            with processed_path.open('rb') as f:
                                analise.img_resultado.save(
                                    f'resultado_{analise.id}{Path(img_file.name).suffix}',
                                    File(f),
                                    save=True
                                )

                        # Atualizar contagens
                        counts = results['class_counts']
                        analise.n_plaquetas = counts['plaqueta']
                        analise.n_celulas_brancas = counts['leucocito']
                        analise.n_celulas_vermelhas = counts['hemacia']
                        analise.n_linfocitos = counts['linfocito']
                        analise.n_monocitos = counts['monocito']
                        analise.n_basofilos = counts['basofilo']
                        analise.n_neutrofilos_banda = counts['neutrofilo_banda']
                        analise.n_neutrofilos_segmentados = counts['neutrofilo_segmentado']
                        analise.n_mielocitos = counts['mielocito']
                        analise.n_metamielocitos = counts['metamielocito']
                        analise.n_promielocitos = counts['promielocito']
                        analise.n_eosinofilos = counts['eosinofilo']
                        
                        analise.acuracia = results['accuracy'] * 100
                        analise.tempo_processamento = results['processing_time']
                        analise.status = 'concluido'
                        analise.save()
                        
                        return JsonResponse({'success': True})
                    else:
                        raise Exception(results.get('error', 'Erro no processamento'))
                
                except Exception as e:
                    analise.status = 'erro'
                    analise.erro_msg = str(e)
                    analise.save()
                    raise

        except Exception as e:
            logger.error(f"Erro ao processar análise: {str(e)}")
            return JsonResponse({
                'success': False, 
                'error': f'Erro ao processar imagem: {str(e)}'
            })

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
    analise = get_object_or_404(Analise, pk=analise_id)
    
    if request.method == 'POST':
        try:
            analise.titulo = request.POST.get('titulo', analise.titulo)
            analise.paciente = request.POST.get('paciente', analise.paciente)
            analise.save()
            messages.success(request, 'Análise atualizada com sucesso!')
            return redirect('Analises:analises')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar análise: {str(e)}')
    
    return render(request, 'Analises/editar.html', {'analise': analise})

def index(request):
    """View para a página inicial"""
    return render(request, 'Analises/index.html', {
        'original_exists': True  # Simplificado para sempre mostrar o conteúdo
    })