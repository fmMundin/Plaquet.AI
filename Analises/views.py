from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import Analise
from datetime import datetime
import os
import logging
from pathlib import Path
from scripts.infer import run_inference
from django.db import transaction
from django.core.files import File
from django.utils import timezone
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'Analises/index.html')  # Landing page

def analises(request):
    analises = Analise.objects.all().distinct()
    return render(request, 'Analises/analises.html', {'analises': analises})

def criar_analise(request):
    if request.method == 'POST':
        with transaction.atomic():
            try:
                if 'img' not in request.FILES:
                    return JsonResponse({
                        'success': False,
                        'error': 'Nenhuma imagem enviada'
                    })

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

    return redirect('analises')

def deletar_analise(request, analise_id):
    if request.method == 'POST':
        analise = get_object_or_404(Analise, pk=analise_id)
        try:
            if analise.img:
                analise.img.delete()
            if analise.img_resultado:
                analise.img_resultado.delete()
            analise.delete()
            messages.success(request, 'Análise excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir análise: {str(e)}')
    return redirect('analises')
