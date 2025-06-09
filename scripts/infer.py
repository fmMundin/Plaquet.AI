from ultralytics import YOLO
import cv2
import time
from pathlib import Path
import numpy as np
import torch

def process_image(weights_path, image_path, output_dir):
    """Processa uma imagem usando o modelo YOLOv8"""
    try:
        # MOdelo foi feito para rodar em  GPU ou CPU
        if torch.cuda.is_available(): 
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False

        model = YOLO(weights_path)
        model.fuse()  
        
        
        model.conf = 0.25  
        model.iou = 0.45  
        
        start_time = time.time()
        
        
        results = model(image_path, verbose=False)[0]  
        processing_time = time.time() - start_time

       
        class_counts = {
            'RBC': 0, 'WBC': 0, 'Platelets': 0,
            'Lymphocyte': 0, 'Monocyte': 0, 'Basophil': 0,
            'Band_Neutrophil': 0, 'Segmented_Neutrophil': 0,
            'Myelocyte': 0, 'Metamyelocyte': 0,
            'Promyelocyte': 0, 'Eosinophil': 0
        }

        
        boxes = results.boxes
        total_detections = len(boxes)
        if total_detections > 0:
           
            classes = boxes.cls.cpu().numpy().astype(int)
            confs = boxes.conf.cpu().numpy()
            total_confidence = confs.sum() * 100  

            
            class_mapping = {
                'hemacia': 'RBC',
                'plaqueta': 'Platelets',
                'leucocito': 'WBC',
                'linfocito': ['Lymphocyte', 'WBC'],
                'monocito': ['Monocyte', 'WBC'],
                'basofilo': ['Basophil', 'WBC'],
                'neutrofilo_banda': ['Band_Neutrophil', 'WBC'],
                'neutrofilo_segmentado': ['Segmented_Neutrophil', 'WBC'],
                'mielocito': ['Myelocyte', 'WBC'],
                'metamielocito': ['Metamyelocyte', 'WBC'],
                'promielocito': ['Promyelocyte', 'WBC'],
                'eosinofilo': ['Eosinophil', 'WBC']
            }

            
            for cls_id in classes:
                class_name = results.names[cls_id]
                mapped_classes = class_mapping.get(class_name, [])
                if isinstance(mapped_classes, list):
                    for mapped_class in mapped_classes:
                        class_counts[mapped_class] += 1
                else:
                    class_counts[mapped_classes] += 1

        
        output_path = Path(output_dir) / f"detected_{Path(image_path).name}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        res_plotted = results.plot(line_width=1)  
        cv2.imwrite(str(output_path), res_plotted, [cv2.IMWRITE_JPEG_QUALITY, 90])  # Comprimir imagem

        return {
            'success': True,
            'class_counts': class_counts,
            'processing_time': processing_time,
            'accuracy': round(total_confidence / total_detections if total_detections > 0 else 0, 2),
            'output_path': str(output_path)
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
