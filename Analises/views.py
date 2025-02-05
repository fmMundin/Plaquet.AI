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
def analises(request):  # mudado de index para analises
    analises = Analise.objects.all().distinct()
    return render(request, 'Analises/analises.html', {'analises': analises})  # mudado index.html para analises.html

def criar_analise(request):
    if request.method == 'POST':
        with transaction.atomic():
            try:
                # Validar arquivo
                if 'img' not in request.FILES:
                    return JsonResponse({
                        'success': False,
                        'error': 'Nenhuma imagem enviada'
                    })

                # Criar análise inicial
                analise = Analise.objects.create(
                    titulo=request.POST['titulo'],
                    paciente=request.POST['paciente'],
                    img=request.FILES['img'],
                    status='processando'
                )

                try:
                    # Configurar caminhos
                    base_dir = Path(__file__).resolve().parent.parent
                    weights_path = str(base_dir / 'scripts' / 'best.pt')
                    output_dir = str(base_dir / 'media' / 'resultados')

                    # Validar arquivos
                    for path in [weights_path, analise.img.path]:
                        if not os.path.exists(path):
                            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

                    # Executar inferência
                    results = run_inference(weights_path, str(analise.img.path), output_dir)

                    # Atualizar análise com resultados
                    analise.n_plaquetas = int(results['class_counts'].get('Platelets', 0))
                    analise.n_celulas_brancas = int(results['class_counts'].get('WBC', 0))
                    analise.n_celulas_vermelhas = int(results['class_counts'].get('RBC', 0))
                    analise.acuracia = float(results['precisao'])
                    analise.tempo_processamento = round(float(results['processing_time']), 2)
                    analise.densidade_relativa = results['densidade_relativa']
                    analise.status = 'concluido'
                    analise.data_analise = datetime.now(tz=ZoneInfo("America/Sao_Paulo"))

                    # Salvar imagem resultado
                    result_path = Path(output_dir) / 'inference_output' / os.path.basename(analise.img.path)
                    if result_path.exists():
                        with open(result_path, 'rb') as f:
                            analise.img_resultado.save(
                                f"resultado_{analise.id}.jpg",
                                File(f),
                                save=False
                            )

                    analise.save()

                    # Após análise bem sucedida, copiar para static
                    if analise.status == 'concluido':
                        static_img_dir = settings.BASE_DIR / 'static' / 'images'
                        static_img_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Copiar imagem original
                        if analise.img:
                            shutil.copy2(
                                analise.img.path,
                                static_img_dir / 'original.png'
                            )
                        
                        # Copiar imagem resultado
                        if analise.img_resultado:
                            shutil.copy2(
                                analise.img_resultado.path,
                                static_img_dir / 'detected.png'
                            )

                    return JsonResponse({'success': True})

                except Exception as e:
                    logger.error(f"Erro na análise: {e}", exc_info=True)
                    analise.status = 'erro'
                    analise.erro_msg = str(e)
                    analise.save()
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    })

            except Exception as e:
                logger.error(f"Erro ao criar análise: {e}", exc_info=True)
                return JsonResponse({
                    'success': False,
                    'error': str(e)
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
        return redirect('analises')  # mudado de 'index' para 'analises'

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
    # Atualizado para verificar arquivos .png em vez de .jpg
    static_images_path = os.path.join(settings.BASE_DIR, 'static', 'images')
    images_exist = (
        os.path.exists(os.path.join(static_images_path, 'original.png')) and 
        os.path.exists(os.path.join(static_images_path, 'detected.png'))
    )
    
    return render(request, 'Analises/index.html', {
        'original_exists': images_exist
    })