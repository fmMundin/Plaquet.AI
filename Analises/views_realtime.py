from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Analise
from scripts.real_time_analysis import RealTimeAnalysis
import cv2
import threading
import time
from datetime import datetime
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Variáveis globais para controle do estado da análise em tempo real
rt_analyzer = None
current_camera = None
is_recording = False
recording_path = None

def get_camera():
    """Função auxiliar para obter e configurar a câmera"""
    global current_camera
    if current_camera is None:
        current_camera = cv2.VideoCapture(0)
        if not current_camera.isOpened():
            logger.error("Erro ao abrir câmera")
            return None
    return current_camera

def release_camera():
    """Função auxiliar para liberar a câmera"""
    global current_camera
    if current_camera:
        current_camera.release()
        current_camera = None

def get_frame():
    """Gera frames da câmera processados pelo analisador"""
    global rt_analyzer, current_camera
    
    camera = get_camera()
    if camera is None:
        return None
        
    if rt_analyzer is None:
        rt_analyzer = RealTimeAnalysis()
    
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        # Processar frame com o analisador
        processed_frame, counts = rt_analyzer.process_frame(frame)
        
        # Converter frame para JPEG
        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        if not ret:
            continue
            
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
        
        # Controle de FPS para não sobrecarregar o sistema
        time.sleep(0.033)  # ~30 FPS

@login_required
def realtime_analysis(request):
    """View para a página de análise em tempo real"""
    global rt_analyzer, is_recording, recording_path
    
    if request.method == 'POST':
        action = request.GET.get('action')
        
        if action == 'start_recording':
            try:
                if not is_recording and rt_analyzer:
                    recording_path = rt_analyzer.start_camera_analysis(
                        output_path=str(Path('media/analises/videos/') / f'analise_{datetime.now().strftime("%Y%m%d_%H%M%S")}.avi')
                    )
                    is_recording = True
                    return JsonResponse({'success': True})
            except Exception as e:
                logger.error(f"Erro ao iniciar gravação: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)})
                
        elif action == 'stop_recording':
            try:
                if is_recording and rt_analyzer:
                    video_path = rt_analyzer.stop_camera_analysis()
                    is_recording = False
                    if video_path:
                        # Criar registro da análise
                        analise = Analise.objects.create(
                            titulo=f'Análise em Tempo Real - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}',
                            tipo_analise='tempo_real',
                            status='concluido',
                            video_resultado=video_path
                        )
                        return JsonResponse({
                            'success': True,
                            'video_path': video_path,
                            'analise_id': analise.id
                        })
                    return JsonResponse({'success': True})
            except Exception as e:
                logger.error(f"Erro ao parar gravação: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)})
                
        elif action == 'get_counts':
            if rt_analyzer:
                return JsonResponse({
                    'success': True,
                    'counts': rt_analyzer.get_current_counts()
                })
                
    return render(request, 'Analises/realtime_analysis.html')

@login_required
def video_feed(request):
    """View para o stream de vídeo"""
    try:
        return StreamingHttpResponse(
            get_frame(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        logger.error(f"Erro no stream de vídeo: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def stop_analysis(request):
    """View para parar a análise e liberar recursos"""
    global rt_analyzer, is_recording
    
    try:
        if is_recording:
            rt_analyzer.stop_camera_analysis()
            is_recording = False
            
        release_camera()
        rt_analyzer = None
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Erro ao parar análise: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
