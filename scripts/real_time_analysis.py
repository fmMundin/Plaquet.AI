from ultralytics import YOLO
import cv2
import numpy as np
import torch
import time
from datetime import datetime
import os
from pathlib import Path

class RealTimeAnalysis:
    def __init__(self, weights_path='scripts/best.pt'):
        # Carregar o modelo YOLO
        self.model = YOLO(weights_path)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Configurações para melhor performance
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
        
        # Configurar modelo para inferência rápida
        self.model.conf = 0.25  # threshold de confiança
        self.model.iou = 0.45   # threshold IOU
        
        # Cores para visualização (RGB)
        self.colors = {
            'hemacia': (0, 0, 255),
            'leucocito': (255, 255, 255),
            'plaqueta': (255, 0, 0),
            'linfocito': (0, 255, 0),
            'monocito': (0, 255, 255),
            'basofilo': (255, 0, 255),
            'eritroblasto': (128, 0, 0),
            'neutrofilo_banda': (0, 128, 128),
            'neutrofilo_segmentado': (128, 128, 0),
            'mielocito': (128, 0, 128),
            'metamielocito': (0, 128, 0),
            'promielocito': (192, 192, 192),
            'eosinofilo': (128, 128, 128)
        }
        
        self.class_counts = {}
        self.reset_counts()

    def reset_counts(self):
        """Resetar contadores de células"""
        self.class_counts = {
            'RBC': 0, 'WBC': 0, 'Platelets': 0,
            'Lymphocyte': 0, 'Monocyte': 0, 'Basophil': 0,
            'Band_Neutrophil': 0, 'Segmented_Neutrophil': 0,
            'Myelocyte': 0, 'Metamyelocyte': 0,
            'Promyelocyte': 0, 'Eosinophil': 0
        }

    def process_frame(self, frame):
        """Processar um frame do vídeo"""
        # Fazer inferência
        results = self.model(frame, verbose=False)[0]
        
        # Processar resultados
        boxes = results.boxes
        processed_frame = frame.copy()
        
        if len(boxes) > 0:
            # Processar detecções
            classes = boxes.cls.cpu().numpy().astype(int)
            confs = boxes.conf.cpu().numpy()
            
            # Resetar contadores para este frame
            self.reset_counts()
            
            # Mapear e contar classes
            for cls_id in classes:
                class_name = results.names[cls_id]
                if class_name == 'hemacia':
                    self.class_counts['RBC'] += 1
                elif class_name == 'plaqueta':
                    self.class_counts['Platelets'] += 1
                elif class_name in ['leucocito', 'linfocito', 'monocito', 'basofilo', 
                                'neutrofilo_banda', 'neutrofilo_segmentado', 'mielocito',
                                'metamielocito', 'promielocito', 'eosinofilo']:
                    self.class_counts['WBC'] += 1
                    
                    # Contar tipos específicos de WBC
                    if class_name == 'linfocito':
                        self.class_counts['Lymphocyte'] += 1
                    elif class_name == 'monocito':
                        self.class_counts['Monocyte'] += 1
                    elif class_name == 'basofilo':
                        self.class_counts['Basophil'] += 1
                    elif class_name == 'neutrofilo_banda':
                        self.class_counts['Band_Neutrophil'] += 1
                    elif class_name == 'neutrofilo_segmentado':
                        self.class_counts['Segmented_Neutrophil'] += 1
                    elif class_name == 'mielocito':
                        self.class_counts['Myelocyte'] += 1
                    elif class_name == 'metamielocito':
                        self.class_counts['Metamyelocyte'] += 1
                    elif class_name == 'promielocito':
                        self.class_counts['Promyelocyte'] += 1
                    elif class_name == 'eosinofilo':
                        self.class_counts['Eosinophil'] += 1
            
            # Desenhar as detecções
            processed_frame = results.plot(line_width=1)
            
        return processed_frame, self.class_counts

    def start_camera_analysis(self, camera_index=0, output_path=None):
        """Iniciar análise em tempo real usando a câmera"""
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Erro ao abrir câmera {camera_index}")
            return
        
        # Configurar gravação de vídeo se necessário
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, 20.0, 
                                (int(cap.get(3)), int(cap.get(4))))
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Processar frame
                processed_frame, counts = self.process_frame(frame)
                
                # Adicionar contagens ao frame
                y_pos = 30
                for cell_type, count in counts.items():
                    text = f"{cell_type}: {count}"
                    cv2.putText(processed_frame, text, (10, y_pos), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    y_pos += 25
                
                # Mostrar frame
                cv2.imshow('Análise em Tempo Real', processed_frame)
                
                # Gravar frame se necessário
                if output_path:
                    out.write(processed_frame)
                
                # Apertar 'q' para sair
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        finally:
            cap.release()
            if output_path:
                out.release()
            cv2.destroyAllWindows()

    def analyze_video(self, video_path, output_path=None):
        """Analisar um arquivo de vídeo"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Erro ao abrir vídeo: {video_path}")
            return
        
        # Configurar gravação de vídeo se necessário
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                                (int(cap.get(3)), int(cap.get(4))))
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Processar frame
                processed_frame, counts = self.process_frame(frame)
                
                # Adicionar contagens ao frame
                y_pos = 30
                for cell_type, count in counts.items():
                    text = f"{cell_type}: {count}"
                    cv2.putText(processed_frame, text, (10, y_pos), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    y_pos += 25
                
                # Mostrar frame
                cv2.imshow('Análise de Vídeo', processed_frame)
                
                # Gravar frame se necessário
                if output_path:
                    out.write(processed_frame)
                
                # Apertar 'q' para sair
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        finally:
            cap.release()
            if output_path:
                out.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    # Exemplo de uso
    analyzer = RealTimeAnalysis()
    
    # Para usar a câmera (o número 0 geralmente é a câmera padrão)
    # analyzer.start_camera_analysis(camera_index=0, output_path='output_camera.avi')
    
    # Para analisar um arquivo de vídeo
    # analyzer.analyze_video('caminho_do_video.mp4', 'output_video.avi')
