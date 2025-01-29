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

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    analises = Analise.objects.all().distinct()
    return render(request, 'Analises/index.html', {'analises': analises})

def criar_analise(request):
    if request.method == 'POST':
        with transaction.atomic():  # Usar transação atômica
            try:
                # Verificar se já existe análise com mesmo título e paciente
                titulo = request.POST['titulo']
                paciente = request.POST['paciente']
                if Analise.objects.filter(titulo=titulo, paciente=paciente).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Já existe uma análise com este título para este paciente'
                    })

                # Criar análise inicial
                analise = Analise.objects.create(
                    titulo=titulo,
                    paciente=paciente,
                    img=request.FILES['img'],
                    status='processando'
                )
                
                logger.info(f"Análise criada: ID {analise.id}")

                try:
                    # Configurar caminhos absolutos
                    base_dir = Path(__file__).resolve().parent.parent
                    weights_path = str(base_dir / 'scripts' / 'best.pt')  # Caminho atualizado
                    output_dir = str(base_dir / 'media' / 'resultados')
                    
                    logger.info(f"Paths configurados - Weights: {weights_path}, Output: {output_dir}")
                    logger.info(f"Imagem path: {analise.img.path}")

                    # Verificar se os arquivos existem
                    if not os.path.exists(weights_path):
                        raise FileNotFoundError(f"Arquivo de modelo não encontrado: {weights_path}")
                    if not os.path.exists(analise.img.path):
                        raise FileNotFoundError(f"Arquivo de imagem não encontrado: {analise.img.path}")

                    # Executar inferência
                    results = run_inference(weights_path, analise.img.path, output_dir)
                    logger.info(f"Resultados da inferência: {results}")

                    # Atualizar análise com resultados
                    analise.n_plaquetas = results['class_counts'].get('Platelets', 0)
                    analise.n_celulas_brancas = results['class_counts'].get('WBC', 0)
                    analise.n_celulas_vermelhas = results['class_counts'].get('RBC', 0)
                    analise.acuracia = results['precisao']
                    analise.tempo_processamento = round(results['processing_time'], 2)
                    analise.data_analise = datetime.now()
                    analise.status = 'concluido'
                    
                    # Salvar imagem resultado
                    result_img_path = Path(output_dir) / 'inference_output' / analise.img.name
                    if result_img_path.exists():
                        with open(result_img_path, 'rb') as f:
                            analise.img_resultado.save(
                                f"resultado_{analise.img.name}",
                                f
                            )
                    
                    analise.save()
                    logger.info("Análise concluída com sucesso")

                    return JsonResponse({
                        'success': True,
                        'message': 'Análise concluída com sucesso!',
                        'resultados': results
                    })

                except Exception as e:
                    logger.error(f"Erro durante a análise: {str(e)}", exc_info=True)
                    analise.status = 'erro'
                    analise.erro_msg = str(e)
                    analise.save()
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    })

            except Exception as e:
                logger.error(f"Erro ao criar análise: {str(e)}", exc_info=True)
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })

    return redirect('index')

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