from ultralytics import YOLO
import cv2
import time
from pathlib import Path
import numpy as np

def process_image(weights_path, image_path, output_dir):
    """Processa uma imagem usando o modelo YOLOv8"""
    try:
        # Carregar modelo e fazer inferência
        model = YOLO(weights_path)
        start_time = time.time()
        results = model(image_path)[0]
        processing_time = time.time() - start_time

        # Inicializar contadores
        class_counts = {
            'RBC': 0, 'WBC': 0, 'Platelets': 0,
            'Lymphocyte': 0, 'Monocyte': 0, 'Basophil': 0,
            'Band_Neutrophil': 0, 'Segmented_Neutrophil': 0,
            'Myelocyte': 0, 'Metamyelocyte': 0,
            'Promyelocyte': 0, 'Eosinophil': 0
        }
        total_confidence = 0

        # Processar cada detecção
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = results.names[cls_id]
            total_confidence += conf

            # Mapear classes
            if class_name == 'hemacia':
                class_counts['RBC'] += 1
            elif class_name == 'plaqueta':
                class_counts['Platelets'] += 1
            elif class_name == 'leucocito':
                class_counts['WBC'] += 1
            elif class_name == 'linfocito':
                class_counts['Lymphocyte'] += 1
                class_counts['WBC'] += 1
            elif class_name == 'monocito':
                class_counts['Monocyte'] += 1
                class_counts['WBC'] += 1
            elif class_name == 'basofilo':
                class_counts['Basophil'] += 1
                class_counts['WBC'] += 1
            elif class_name == 'neutrofilo_banda':
                class_counts['Band_Neutrophil'] += 1
                class_counts['WBC'] += 1
            elif class_name == 'neutrofilo_segmentado':
                class_counts['Segmented_Neutrophil'] += 1
                class_counts['WBC'] += 1
            elif class_name == 'mielocito':
                class_counts['Myelocyte'] += 1
                class_counts['WBC'] += 1
            elif class_name == 'metamielocito':
                class_counts['Metamyelocyte'] += 1
                class_counts['WBC'] += 1
            elif class_name == 'promielocito':
                class_counts['Promyelocyte'] += 1
                class_counts['WBC'] += 1
            elif class_name == 'eosinofilo':
                class_counts['Eosinophil'] += 1
                class_counts['WBC'] += 1

        # Calcular acurácia média
        num_detections = len(results.boxes)
        accuracy = (total_confidence / num_detections * 100) if num_detections > 0 else 0

        # Salvar imagem com detecções
        output_path = Path(output_dir) / f"detected_{Path(image_path).name}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        res_plotted = results.plot()
        cv2.imwrite(str(output_path), res_plotted)

        return {
            'success': True,
            'class_counts': class_counts,
            'accuracy': accuracy,
            'processing_time': processing_time,
            'output_path': str(output_path)
        }

    except Exception as e:
        print(f"Erro no processamento: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
