import torch
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import cv2
import time

class AnalysisService:
    def __init__(self):
        self.model = YOLO('scripts/best.pt')
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.class_names = {
            0: 'hemacia',
            1: 'leucocito',
            2: 'plaqueta',
            3: 'linfocito',
            4: 'monocito',
            5: 'basofilo',
            6: 'eritroblasto',
            7: 'neutrofilo_banda',
            8: 'neutrofilo_segmentado',
            9: 'mielocito',
            10: 'metamielocito',
            11: 'promielocito',
            12: 'eosinofilo'
        }
    
    def process_image(self, image_path):
        """Método único para processar imagem e retornar resultados"""
        try:
            start_time = time.time()
            
            # Carregar e verificar imagem
            image = cv2.imread(str(image_path))
            if image is None:
                return {'success': False, 'error': 'Erro ao carregar imagem'}

            # Fazer predição
            results = self.model(image)[0]
            
            # Contagem de células
            cell_counts = {name: 0 for name in self.class_names.values()}
            for box in results.boxes:
                cls_id = int(box.cls[0])
                class_name = self.class_names[cls_id]
                cell_counts[class_name] += 1

            # Preparar resultados
            return {
                'success': True,
                'cell_counts': cell_counts,
                'processing_time': time.time() - start_time,
                'accuracy': float(results.boxes.conf.mean() if len(results.boxes) > 0 else 0)
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

# Instância global do serviço
analysis_service = AnalysisService()
