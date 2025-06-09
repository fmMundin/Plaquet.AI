from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
import argparse
import pandas as os

def detect_cells(image_path):
    # Carregar melhor modelo
    model_path = Path("runs_train/yolov8x_blood_cells_20250301_1924/weights/best.pt")
    if not model_path.exists():
        raise FileNotFoundError(f"Modelo não encontrado em: {model_path}")
    
    # Classes e cores (BGR)
    classes = {
        0: ("RBC", (0, 0, 255)),         # Vermelho
        1: ("WBC", (0, 255, 0)),         # Verde
        2: ("PLT", (255, 0, 0)),         # Azul
        3: ("Monocyte", (0, 255, 255)),  # Amarelo
        4: ("Eosinophil", (255, 0, 255)), # Magenta
        5: ("Basophil", (128, 0, 128)),  # Roxo
        6: ("Promyelocyte", (0, 255, 255)), # Ciano
        7: ("Myelocyte", (0, 128, 0)),   # Verde escuro
        8: ("Metamyelocyte", (128, 128, 0)) # Verde-azulado
    }
    
    # Carregar modelo e imagem
    model = YOLO(str(model_path))
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
    
    # Fazer predições
    results = model(image, conf=0.4)[0]  # Confidence threshold 0.4
    
    # Processar resultados
    detections = {'total': 0}
    annotated_img = image.copy()
    
    # Desenhar boxes e contar detecções
    for box in results.boxes:
        cls = int(box.cls)
        conf = float(box.conf)
        
        if cls in classes:
            detections['total'] += 1
            detections[cls] = detections.get(cls, 0) + 1
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_name, color = classes[cls]
            label = f"{class_name} {conf:.2f}"
            
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 2)
            cv2.rectangle(annotated_img, (x1, y1-25), (x1+len(label)*9, y1), color, -1)
            cv2.putText(annotated_img, label, (x1, y1-5),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    # Salvar resultado
    output_path = Path(image_path).parent / f"detected_{Path(image_path).name}"
    cv2.imwrite(str(output_path), annotated_img)
    
    # Mostrar resultados
    print("\nDetecções:")
    print(f"Total de células: {detections['total']}")
    for cls_id, count in detections.items():
        if cls_id != 'total' and cls_id in classes:
            class_name = classes[cls_id][0]
            percentage = (count/detections['total'])*100
            print(f"{class_name}: {count} ({percentage:.1f}%)")
    
    print(f"\nImagem com detecções salva em: {output_path}")
    return detections

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detector de Células Sanguíneas")
    parser.add_argument("image", help="Caminho para a imagem a ser analisada")
    args = parser.parse_args()
    
    try:
        detect_cells(args.image)
    except Exception as e:
        print(f"Erro: {e}")
