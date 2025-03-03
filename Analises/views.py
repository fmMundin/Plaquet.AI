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
                # Verificar se um arquivo foi enviado
                if 'img' not in request.FILES:
                    return JsonResponse({'success': False, 'error': 'Nenhuma imagem foi enviada'})
                
                img_file = request.FILES['img']
                # Verificar extensão do arquivo
                ext = img_file.name.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png']:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Formato de imagem inválido. Use JPG, JPEG ou PNG'
                    })

                analise = Analise(
                    titulo=request.POST['titulo'],
                    paciente=request.POST['paciente'],
                    img=img_file,
                    status='processando',
                    data_analise=timezone.now()
                )
                analise.save()

                # Garantir que o diretório de resultados existe
                result_dir = settings.MEDIA_ROOT / 'resultados'
                result_dir.mkdir(exist_ok=True, parents=True)

                try:
                    # Configurar caminhos
                    base_dir = Path(__file__).resolve().parent.parent
                    weights_path = str(base_dir / 'scripts' / 'best.pt')
                    output_dir = str(base_dir / 'media' / 'resultados')

                    # Validar arquivos
                    for path in [weights_path, analise.img.path]:
                        if not os.path.exists(path):
                            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

                    # Processar imagem
                    logger.info(f"Iniciando processamento da imagem: {analise.img.path}")
                    results = process_image(weights_path, str(analise.img.path), output_dir)
                    
                    if results['success']:  # Removida a verificação de 'processed_image_path'
                        logger.info("Imagem processada com sucesso")
                        
                        # Salvar imagem processada
                        processed_path = Path(results['output_path'])  # Usando 'output_path' ao invés de 'processed_image_path'
                        if processed_path.exists():
                            with processed_path.open('rb') as f:
                                analise.img_resultado.save(
                                    f'resultado_{analise.id}.{ext}',
                                    File(f),
                                    save=True
                                )
                                logger.info(f"Imagem resultado salva: {analise.img_resultado.path}")
                        else:
                            raise Exception("Arquivo de resultado não foi gerado")

                        # Atualizar análise com resultados detalhados
                        analise.n_plaquetas = results['class_counts']['Platelets']
                        analise.n_celulas_brancas = results['class_counts']['WBC']
                        analise.n_celulas_vermelhas = results['class_counts']['RBC']
                        analise.n_linfocitos = results['class_counts']['Lymphocyte']
                        analise.n_monocitos = results['class_counts']['Monocyte']
                        analise.n_basofilos = results['class_counts']['Basophil']
                        analise.n_neutrofilos_banda = results['class_counts']['Band_Neutrophil']
                        analise.n_neutrofilos_segmentados = results['class_counts']['Segmented_Neutrophil']
                        analise.n_mielocitos = results['class_counts']['Myelocyte']
                        analise.n_metamielocitos = results['class_counts']['Metamyelocyte']
                        analise.n_promielocitos = results['class_counts']['Promyelocyte']
                        analise.n_eosinofilos = results['class_counts']['Eosinophil']
                        analise.acuracia = results.get('accuracy', 0) * 100
                        analise.tempo_processamento = results.get('processing_time', 0)
                        analise.status = 'concluido'
                        analise.save()
                        
                        return JsonResponse({'success': True})
                    else:
                        raise Exception(results.get('error', 'Erro desconhecido no processamento'))
                
                except Exception as e:
                    analise.status = 'erro'
                    analise.erro_msg = str(e)
                    analise.save()
                    raise  # Re-raise para ser capturado pelo try externo

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