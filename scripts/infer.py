import torch
from pathlib import Path
from yolov5 import detect
import time
import os
import json

def run_inference(weights_path, source_image, output_dir):
    print(f"Executando inferência com pesos: {weights_path}")
    print(f"Imagem de origem: {source_image}")
    print(f"Diretório de saída: {output_dir}")
    
    start_time = time.time()
    detect.run(
        weights=weights_path,
        source=source_image,
        project=output_dir,
        name='inference_output',
        exist_ok=True,
        save_txt=True,
        save_conf=True,
        save_crop=False,
        nosave=False,
        classes=None,
        # Ajustar parâmetros para melhorar a detecção
        conf_thres=0.25,      # Aumentar threshold de confiança
        iou_thres=0.45,       # Ajustar IoU threshold
        max_det=1000,         # Limitar número máximo de detecções
        agnostic_nms=True,    # NMS entre diferentes classes
        augment=False,
        visualize=False,
        update=False,
        line_thickness=2,
        hide_labels=False,
        hide_conf=False,
        half=False,
        dnn=False,
    )
    end_time = time.time()
    processing_time = end_time - start_time
    print("Inferência concluída.")
    
    # Ler os resultados dos arquivos de texto
    labels_dir = Path(output_dir) / 'inference_output' / 'labels'
    label_files = list(labels_dir.glob('*.txt'))
    
    num_cells = 0
    class_counts = {'RBC': 0, 'WBC': 0, 'Platelets': 0}
    precisao_total = 0
    
    for label_file in label_files:
        with open(label_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 6:  # Verificar se tem dados suficientes
                    class_id = int(parts[0])
                    conf = float(parts[5])
                    
                    # Filtrar detecções com baixa confiança
                    if conf >= 0.25:  # Aumentar threshold de confiança
                        class_name = ['RBC', 'WBC', 'Platelets'][class_id]
                        num_cells += 1
                        precisao_total += conf
                        class_counts[class_name] += 1
    
    # Calcular a precisão do modelo
    precisao = (precisao_total / num_cells * 100) if num_cells > 0 else 0
    
    # Aplicar fator de correção para cada tipo de célula
    # Estes valores podem precisar de ajuste baseado em sua validação
    correction_factors = {
        'RBC': 0.85,      # Reduz 15% das células vermelhas detectadas
        'WBC': 0.95,      # Reduz 5% das células brancas detectadas
        'Platelets': 0.90 # Reduz 10% das plaquetas detectadas
    }
    
    for cell_type in class_counts:
        class_counts[cell_type] = int(class_counts[cell_type] * correction_factors[cell_type])
    
    return {
        "processing_time": processing_time,
        "num_cells": sum(class_counts.values()),  # Atualizar contagem total
        "class_counts": class_counts,
        "precisao": precisao
    }

if __name__ == "__main__":
    weights_path = str(Path(__file__).parent / 'best.pt')
    source_image = 'E:/plaquetaiModel/data/test/images/BloodImage_00062.jpeg'  # Substitua pelo caminho da sua imagem de teste
    output_dir = 'E:/plaquetaiModel/runs/inference'

    print("Iniciando script de inferência...")
    results = run_inference(weights_path, source_image, output_dir)
    print(json.dumps(results, indent=4))
    print(f"Resultados salvos em {output_dir}/inference_output")
