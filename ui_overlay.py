import cv2
import numpy as np
import time

def get_ui_texture(is_loading):
    """
    Genera una imagen RGBA transparente con los botones dibujados.
    """
    # Crear imagen transparente RGBA de 350x100 pixels (suficiente para los botones)
    img = np.zeros((100, 350, 4), dtype=np.uint8)
    
    # Botón Abrir Modelo (x=10 a 160, y=10 a 40)
    cv2.rectangle(img, (10, 10), (160, 40), (40, 40, 40, 200), -1)
    cv2.rectangle(img, (10, 10), (160, 40), (200, 200, 200, 255), 1)
    cv2.putText(img, "Abrir Modelo", (20, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255, 255), 1)
    
    # Botón Cambiar Vista (x=170 a 320, y=10 a 40)
    cv2.rectangle(img, (170, 10), (320, 40), (40, 40, 40, 200), -1)
    cv2.rectangle(img, (170, 10), (320, 40), (200, 200, 200, 255), 1)
    cv2.putText(img, "Vista (V)", (180, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255, 255), 1)
    
    # Indicador de carga animado (solo aparece si is_loading es True)
    if is_loading:
        dots = int(time.time() * 3) % 4
        loading_text = "Cargando" + "." * dots
        cv2.rectangle(img, (10, 50), (160, 80), (30, 30, 30, 200), -1)
        cv2.rectangle(img, (10, 50), (160, 80), (0, 200, 255, 255), 1)
        cv2.putText(img, loading_text, (20, 70), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 200, 255, 255), 1)
        
    return img
