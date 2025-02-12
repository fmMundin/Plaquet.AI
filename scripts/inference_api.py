import torch
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import cv2
import time

class BloodCellPredictor:
    def __init__(self, weights_path='scripts/best.pt'):
        self.model = YOLO(weights_path)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Atualizado conforme novo YAML
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
        
        self.colors = {
            cls_id: tuple(np.random.randint(0, 255, 3).tolist())
            for cls_id in self.class_names
        }

    def predict_image(self, image_path, conf_thres=0.25, iou_thres=0.45):
        try:
            start_time = time.time()
            
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Imagem não pôde ser carregada")

            # Usando os mesmos nomes de parâmetros que o YOLO espera
            results = self.model(image, conf=conf_thres, iou=iou_thres)[0]
            
            # Processar resultados
            detections = []
            cell_counts = {name: 0 for name in self.class_names.values()}
            
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.class_names[cls_id]
                
                cell_counts[class_name] += 1
                
                # Desenhar detecções
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                color = self.colors[cls_id]
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                label = f"{class_name} {conf:.2f}"
                cv2.putText(image, label, (x1, y1-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            processing_time = time.time() - start_time

            return {
                'success': True,
                'detections': len(detections),
                'cell_counts': cell_counts,
                'annotated_image': image,
                'processing_time': processing_time,
                'accuracy': float(results.boxes.conf.mean() if len(results.boxes) > 0 else 0)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Função auxiliar para executar inferência
def run_inference(image_path, conf_thres=0.25, iou_thres=0.45):
    """
    Função auxiliar para executar inferência
    Args:
        image_path (str): Caminho da imagem
        conf_thres (float): Limiar de confiança (0-1)
        iou_thres (float): Limiar de IoU (0-1)
    Returns:
        dict: Resultados da inferência
    """
    predictor = BloodCellPredictor()
    return predictor.predict_image(image_path, conf_thres=conf_thres, iou_thres=iou_thres)
