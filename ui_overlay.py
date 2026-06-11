import cv2
import numpy as np
import time
import config

def get_ui_texture(is_loading):
    """
    Genera una imagen RGBA transparente con los botones dibujados.
    Ahora incluye los botones para los modos de la Fase 3.
    """
    img = np.zeros((200, 820, 4), dtype=np.uint8)
    
    # Botón Abrir Modelo (x=10 a 160)
    cv2.rectangle(img, (10, 10), (160, 40), (40, 40, 40, 200), -1)
    cv2.rectangle(img, (10, 10), (160, 40), (200, 200, 200, 255), 1)
    cv2.putText(img, "Abrir Modelo", (20, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255, 255), 1)
    
    # Botón Cambiar Vista (x=170 a 320)
    cv2.rectangle(img, (170, 10), (320, 40), (40, 40, 40, 200), -1)
    cv2.rectangle(img, (170, 10), (320, 40), (200, 200, 200, 255), 1)
    cv2.putText(img, "Vista (V)", (180, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255, 255), 1)
    
    # Botón Modo Renderizado (x=330 a 480)
    mode_str = config.render_modes[config.current_render_mode_idx]
    cv2.rectangle(img, (330, 10), (480, 40), (40, 40, 40, 200), -1)
    cv2.rectangle(img, (330, 10), (480, 40), (200, 200, 200, 255), 1)
    cv2.putText(img, f"Modo (M)", (340, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255, 255), 1)
    
    # Botón Grid Suelo (x=490 a 640)
    grid_str = "Grid: ON" if config.show_grid else "Grid: OFF"
    cv2.rectangle(img, (490, 10), (640, 40), (40, 40, 40, 200), -1)
    cv2.rectangle(img, (490, 10), (640, 40), (200, 200, 200, 255), 1)
    cv2.putText(img, grid_str, (500, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255, 255), 1)
    
    # Indicador de carga animado
    if is_loading:
        dots = int(time.time() * 3) % 4
        loading_text = "Cargando" + "." * dots
        cv2.rectangle(img, (10, 50), (160, 80), (30, 30, 30, 200), -1)
        cv2.rectangle(img, (10, 50), (160, 80), (0, 200, 255, 255), 1)
        cv2.putText(img, loading_text, (20, 70), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 200, 255, 255), 1)
        
    # Mostrar gesto actual (Modo Debug Fase 4)
    if config.detected_gestures:
        gestures_str = ", ".join(config.detected_gestures)
        cv2.putText(img, f"Gesto: {gestures_str}", (10, 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0, 255), 2)
        
    # Botón Gestos (x=650 a 800)
    gestos_str = "Gestos" if config.show_gestures_menu else "Gestos"
    cv2.rectangle(img, (650, 10), (800, 40), (40, 40, 40, 200), -1)
    if config.show_gestures_menu:
        cv2.rectangle(img, (650, 10), (800, 40), (0, 255, 0, 255), 2)
    else:
        cv2.rectangle(img, (650, 10), (800, 40), (200, 200, 200, 255), 1)
    cv2.putText(img, gestos_str, (695, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255, 255), 1)
        
    # Leyenda de Gestos
    if config.show_gestures_menu:
        start_y = 70
        cv2.putText(img, "Gestos Disponibles:", (650, start_y), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255, 255), 1)
        cv2.putText(img, "- Palma: Mover/Rotar", (650, start_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- Pulgar+Indice: Zoom", (650, start_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- Pulgar Arriba: Modo", (650, start_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- 2 Dedos (V): Rotar Z", (650, start_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- 2 Manos: Reset", (650, start_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        
    return img
