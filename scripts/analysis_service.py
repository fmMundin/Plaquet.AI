import torch
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import cv2
import time
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.model = YOLO('scripts/best.pt')
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.logger = logging.getLogger(__name__)
        
        # Define cores para cada classe
        self.colors = {
            'hemacia': (0, 0, 255),      # Vermelho
            'leucocito': (255, 255, 255), # Branco
            'plaqueta': (255, 0, 0),     # Azul
            'linfocito': (0, 255, 0),    # Verde
            'monocito': (0, 255, 255),   # Amarelo
            'basofilo': (255, 0, 255),   # Magenta
            'eritroblasto': (128, 0, 0),
            'neutrofilo_banda': (0, 128, 128),
            'neutrofilo_segmentado': (128, 128, 0),
            'mielocito': (128, 0, 128),
            'metamielocito': (0, 128, 0),
            'promielocito': (192, 192, 192),
            'eosinofilo': (128, 128, 128)
        }
        
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
    
    def draw_boxes(self, image, results):
        """Desenha as bounding boxes na imagem"""
        img = image.copy()
        
        for box in results.boxes:
            # Extrair coordenadas e classe
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = self.class_names[cls_id]
            
            # Obter cor para a classe
            color = self.colors.get(class_name, (255, 255, 255))
            
            # Desenhar retângulo
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            # Adicionar texto com nome da classe e confiança
            label = f'{class_name} {conf:.2f}'
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img, (x1, y1-20), (x1+w, y1), color, -1)
            cv2.putText(img, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (255, 255, 255), 1, cv2.LINE_AA)
        
        return img

    def process_image(self, image_path):
        """Processa a imagem e retorna resultados"""
        try:
            self.logger.info(f"Iniciando processamento da imagem: {image_path}")
            start_time = datetime.now()
            
            # Verificar se o arquivo existe
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")

            # Carregar e verificar imagem
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError("Erro ao ler imagem. Verifique se é um arquivo válido.")

            # Criar diretório para resultado se não existir
            result_dir = Path(image_path).parent / 'resultados'
            result_dir.mkdir(exist_ok=True, parents=True)

            # Gerar nome do arquivo de resultado
            result_path = result_dir / f"detected_{Path(image_path).name}"

            # Fazer predição
            results = self.model(image)[0]
            
            # Desenhar bounding boxes
            processed_image = self.draw_boxes(image, results)
            
            # Salvar imagem processada
            cv2.imwrite(str(result_path), processed_image)
            
            # Contagem de células
            cell_counts = {name: 0 for name in self.class_names.values()}
            for box in results.boxes:
                cls_id = int(box.cls[0])
                class_name = self.class_names[cls_id]
                cell_counts[class_name] += 1

            # Calcular tempo de processamento
            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                'success': True,
                'processed_image_path': str(result_path),
                'cell_counts': cell_counts,
                'processing_time': processing_time,
                'accuracy': float(results.boxes.conf.mean() if len(results.boxes) > 0 else 0)
            }

        except Exception as e:
            self.logger.error(f"Erro no processamento: {str(e)}")
            return {'success': False, 'error': str(e)}

# Instância global do serviço
analysis_service = AnalysisService()
