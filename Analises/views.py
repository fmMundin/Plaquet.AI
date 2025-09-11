from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Analise
from datetime import datetime
import os
import logging
from pathlib import Path
from scripts.infer import process_image
import traceback
from django.db import transaction
from django.core.files import File
from django.conf import settings
from django.utils import timezone
import shutil
import time
from scripts.analysis_service import analysis_service
from django.contrib.auth.decorators import login_required

try:
    from scripts.infer import process_image
except ImportError:
    pass
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
                                    f'resultado_{analise.id}.jpg',
                                    File(f),
                                    save=True
                                )

                        # Atualizar dados da análise
                        counts = results['class_counts']
                        analise.n_plaquetas = counts.get('Platelets', 0)
                        analise.n_celulas_brancas = counts.get('WBC', 0)
                        analise.n_celulas_vermelhas = counts.get('RBC', 0)
                        analise.n_linfocitos = counts.get('Lymphocyte', 0)
                        analise.n_monocitos = counts.get('Monocyte', 0)
                        analise.n_basofilos = counts.get('Basophil', 0)
                        analise.n_neutrofilos_banda = counts.get('Band_Neutrophil', 0)
                        analise.n_neutrofilos_segmentados = counts.get('Segmented_Neutrophil', 0)
                        analise.n_mielocitos = counts.get('Myelocyte', 0)
                        analise.n_metamielocitos = counts.get('Metamyelocyte', 0)
                        analise.n_promielocitos = counts.get('Promyelocyte', 0)
                        analise.n_eosinofilos = counts.get('Eosinophil', 0)
                        
                        analise.acuracia = results['accuracy']
                        analise.tempo_processamento = results['processing_time']
                        analise.status = 'concluido'
                        analise.save()
                        
                        logger.info(f"Análise {analise.id} processada com sucesso. Acurácia: {analise.acuracia:.2f}%")
                        return JsonResponse({'success': True})
                    else:
                        raise Exception(results.get('error', 'Erro no processamento'))

                except Exception as e:
                    logger.error(f"Erro no processamento: {str(e)}")
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
        
        # Mapear as contagens para o formato correto
        contagens = {
            'plaquetas': analise.n_plaquetas or 0,
            'celulas_brancas': analise.n_celulas_brancas or 0,
            'celulas_vermelhas': analise.n_celulas_vermelhas or 0,
            'linfocitos': analise.n_linfocitos or 0,
            'monocitos': analise.n_monocitos or 0,
            'basofilos': analise.n_basofilos or 0,
            'eosinofilos': analise.n_eosinofilos or 0,
            'neutrofilos_banda': analise.n_neutrofilos_banda or 0,
            'neutrofilos_segmentados': analise.n_neutrofilos_segmentados or 0
        }
        
        return render(request, 'Analises/detalhes.html', {
            'analise': analise,
            'contagens': contagens
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