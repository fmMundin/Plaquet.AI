from ultralytics import YOLO
import cv2
import time
from pathlib import Path
import numpy as np

def process_image(weights_path, image_path, output_dir):
    """Processa uma imagem usando o modelo YOLOv8"""
    try:
        # Carregar modelo
        model = YOLO(weights_path)
        start_time = time.time()
        
        # Realizar inferência
        results = model(image_path)[0]
        processing_time = time.time() - start_time
        
        # Inicializar contagens
        class_counts = {
            'hemacia': 0,
            'leucocito': 0,
            'plaqueta': 0,
            'linfocito': 0,
            'monocito': 0,
            'basofilo': 0,
            'eritroblasto': 0,
            'neutrofilo_banda': 0,
            'neutrofilo_segmentado': 0,
            'mielocito': 0,
            'metamielocito': 0,
            'promielocito': 0,
            'eosinofilo': 0
        }
        
        # Processar detecções
        total_confidence = 0
        boxes = results.boxes
        
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = results.names[cls]
            
            if class_name in class_counts:
                class_counts[class_name] += 1
                total_confidence += conf
        
        # Salvar imagem com detecções
        output_path = Path(output_dir) / f"detected_{Path(image_path).name}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Plotar resultados
        res_plotted = results.plot()
        cv2.imwrite(str(output_path), res_plotted)
        
        return {
            'success': True,
            'class_counts': class_counts,
            'processing_time': processing_time,
            'accuracy': (total_confidence / len(boxes)) if len(boxes) > 0 else 0,
            'output_path': str(output_path)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
