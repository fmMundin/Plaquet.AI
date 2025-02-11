import torch
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import cv2

class BloodCellPredictor:
    def __init__(self):
        # Carregar modelo uma única vez na inicialização
        model_path = Path('models/best.pt')
        self.model = YOLO(str(model_path))
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Mapeamento de classes
        self.class_names = {
            0: 'hemacia',
            1: 'eosinofilo',
            2: 'plaqueta',
            3: 'linfocito',
            4: 'monocito',
            5: 'basofilo',
            6: 'eritroblasto',
            7: 'neutrofilo_banda',
            8: 'neutrofilo_segmentado',
            9: 'mielocito',
            10: 'metamielocito',
            11: 'promielocito'
        }
        
        # Cores para visualização
        self.colors = {
            cls_id: tuple(np.random.randint(0, 255, 3).tolist())
            for cls_id in self.class_names
        }

    def predict_image(self, image_array, conf_threshold=0.25):
        """
        Realizar predição em uma imagem
        Args:
            image_array: Numpy array da imagem (BGR)
            conf_threshold: Limiar de confiança
        Returns:
            dict: Resultados e imagem com anotações
        """
        # Fazer predição
        results = self.model(image_array, conf=conf_threshold)[0]
        
        # Preparar resultados
        detections = []
        cell_counts = {name: 0 for name in self.class_names.values()}
        
        # Processar cada detecção
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = self.class_names[cls_id]
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            detections.append({
                'class': class_name,
                'confidence': conf,
                'bbox': [x1, y1, x2, y2]
            })
            
            cell_counts[class_name] += 1
            
            # Desenhar bbox e label
            color = self.colors[cls_id]
            cv2.rectangle(image_array, (x1, y1), (x2, y2), color, 2)
            label = f"{class_name} {conf:.2f}"
            cv2.putText(image_array, label, (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return {
            'detections': detections,
            'cell_counts': cell_counts,
            'annotated_image': image_array,
            'total_cells': len(detections)
        }

    def get_cell_distribution(self, cell_counts):
        """Calcular distribuição percentual das células"""
        total = sum(cell_counts.values())
        if total == 0:
            return {}
            
        return {
            cell_type: (count/total * 100)
            for cell_type, count in cell_counts.items()
            if count > 0
        }

# Exemplo de uso (não necessário para integração com Django)
if __name__ == "__main__":
    predictor = BloodCellPredictor()
    
    # Exemplo com uma imagem
    test_image = cv2.imread("data/test/images/test_image.png")
    results = predictor.predict_image(test_image)
    
    print("\nContagem de células:")
    for cell_type, count in results['cell_counts'].items():
        if count > 0:
            print(f"{cell_type}: {count}")
    
    print("\nDistribuição percentual:")
    dist = predictor.get_cell_distribution(results['cell_counts'])
    for cell_type, percentage in dist.items():
        print(f"{cell_type}: {percentage:.1f}%")
