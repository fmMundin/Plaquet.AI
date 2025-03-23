import cv2
import numpy as np
import torch
from PIL import Image
import io

def preprocess_image(image_file, max_size=512):
    try:
        image_file.seek(0)
        image_content = image_file.read()
        nparr = np.frombuffer(image_content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Não foi possível carregar a imagem")

        height, width = img.shape[:2]
        scale = min(max_size/width, max_size/height)
        if scale < 1:
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))

        return img

    except Exception as e:
        raise ValueError(f"Erro no pré-processamento: {str(e)}")

def batch_process_cells(model, images, batch_size=4):
    results = []
    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]
        batch_results = model.predict(np.array(batch))
        results.extend(batch_results)
    return results

def enable_optimization():
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
    
    torch.set_grad_enabled(False)
