from ultralytics import YOLO
import cv2
import time
from pathlib import Path
import numpy as np

def process_image(weights_path, image_path, output_dir):
    """
    Processa uma imagem usando o modelo YOLOv8 e retorna os resultados
    """
    try:
        # Carregar modelo
        model = YOLO(weights_path)
        
        # Tempo inicial
        start_time = time.time()
        
        # Realizar inferência
        results = model(image_path)[0]
        
        # Calcular tempo de processamento
        processing_time = time.time() - start_time
        
        # Atualizar contagens
        class_counts = {
            'RBC': 0,          # células vermelhas
            'WBC': 0,          # células brancas
            'Platelets': 0,    # plaquetas
            'Lymphocyte': 0,   # linfócitos
            'Monocyte': 0,     # monócitos
            'Basophil': 0,     # basófilos
            'Erythroblast': 0, # eritroblastos
            'Band_Neutrophil': 0,
            'Segmented_Neutrophil': 0,
            'Myelocyte': 0,
            'Metamyelocyte': 0,
            'Promyelocyte': 0,
            'Eosinophil': 0
        }
        
        # Processar resultados
        boxes = results.boxes
        total_confidence = 0
        total_detections = len(boxes)
        
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = results.names[cls]
            
            # Mapear classes conforme o modelo atual
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
            elif class_name == 'eritroblasto':
                class_counts['Erythroblast'] += 1
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
            
            total_confidence += conf

        # Calcular densidade relativa
        total_cells = sum(class_counts.values())
        densidade_relativa = {
            k: (v / total_cells * 100) if total_cells > 0 else 0
            for k, v in class_counts.items()
        }
        
        # Salvar imagem com detecções
        img_path = Path(image_path)
        output_path = Path(output_dir) / 'inference_output' / img_path.name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Plotar resultados
        res_plotted = results.plot()
        cv2.imwrite(str(output_path), res_plotted)
        
        return {
            'success': True,
            'class_counts': class_counts,
            'densidade_relativa': densidade_relativa,
            'processing_time': processing_time,
            'precisao': (total_confidence / total_detections * 100) if total_detections > 0 else 0,
            'processed_image_path': str(output_path),  # Adicionada esta linha
            'output_path': str(output_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Remova ou comente esta linha
# run_inference = process_image
