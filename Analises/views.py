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

                # Renomear a imagem se necessário
                if analise.img:
                    nome_original = os.path.basename(analise.img.name)
                    nova_extensao = os.path.splitext(nome_original)[1]
                    novo_nome = f"analise_{analise.id}{nova_extensao}"
                    novo_path = os.path.join('analises', novo_nome)
                    
                    # Renomear o arquivo
                    os.rename(analise.img.path, os.path.join(os.path.dirname(analise.img.path), novo_nome))
                    analise.img.name = novo_path
                    analise.save()  # Salvar novamente com o novo nome

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
                    try:
                        output_dir = Path(settings.MEDIA_ROOT) / 'resultados'
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        result_img_path = Path(output_dir) / 'inference_output' / analise.img.name
                        if result_img_path.exists():
                            novo_nome = f"resultado_{analise.id}_{os.path.basename(analise.img.name)}"
                            novo_path = output_dir / novo_nome
                            
                            # Copiar arquivo para o diretório de mídia
                            import shutil
                            shutil.copy2(result_img_path, novo_path)
                            
                            # Salvar caminho relativo no modelo
                            relativo_path = os.path.join('resultados', novo_nome)
                            analise.img_resultado.name = relativo_path
                            
                    except Exception as img_error:
                        logger.error(f"Erro ao salvar imagem resultado: {str(img_error)}")
                        # Não interromper o processo se falhar ao salvar a imagem
                    
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

def detalhes_analise(request, analise_id):
    try:
        analise = get_object_or_404(Analise, pk=analise_id)
        return render(request, 'Analises/detalhes.html', {
            'analise': analise
        })
    except Exception as e:
        logger.error(f"Erro ao exibir detalhes da análise {analise_id}: {str(e)}", exc_info=True)
        messages.error(request, f'Erro ao exibir detalhes: {str(e)}')
        return redirect('index')

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