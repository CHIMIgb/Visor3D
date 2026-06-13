import cv2
import numpy as np
import time
import config

def get_ui_texture(is_loading):
    """
    Genera una imagen RGBA transparente con los botones y feedback visual.
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
        
    # Mostrar gesto actual
    if config.detected_gestures:
        gestures_str = ", ".join(config.detected_gestures)
        cv2.putText(img, f"Gesto: {gestures_str}", (10, 100), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0, 255), 2)
        
    # Botón Gestos (x=650 a 800)
    cv2.rectangle(img, (650, 10), (800, 40), (40, 40, 40, 200), -1)
    if config.show_gestures_menu:
        cv2.rectangle(img, (650, 10), (800, 40), (0, 255, 0, 255), 2)
    else:
        cv2.rectangle(img, (650, 10), (800, 40), (200, 200, 200, 255), 1)
    cv2.putText(img, "Gestos", (695, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255, 255), 1)
        
    # Leyenda de Gestos
    if config.show_gestures_menu:
        start_y = 70
        cv2.putText(img, "Gestos Disponibles:", (650, start_y), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255, 255), 1)
        cv2.putText(img, "- Palma: Mover/Rotar", (650, start_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- Pulgar+Indice: Zoom", (650, start_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- 2 Indices: Modo", (650, start_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- 2 Dedos (V): Rotar Z", (650, start_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- 2 Manos: Reset", (650, start_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        
    # ====== FEEDBACK FASE 7 ======
    now = time.time()
    
    # Feedback de Color (C)
    if now - config.color_feedback_time < 2.0:
        color_rgb = config.color_palette[config.current_color_idx]
        color_bgra = (int(color_rgb[2]*255), int(color_rgb[1]*255), int(color_rgb[0]*255), 255)
        name = config.color_names[config.current_color_idx]
        cv2.rectangle(img, (10, 120), (180, 155), color_bgra, -1)
        cv2.rectangle(img, (10, 120), (180, 155), (255, 255, 255, 255), 1)
        cv2.putText(img, f"Color: {name}", (18, 143), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
    
    # Indicador Modo Luz (L)
    if config.light_mode:
        cv2.rectangle(img, (190, 120), (340, 155), (0, 200, 255, 200), -1)
        cv2.putText(img, "LUZ ACTIVA", (200, 143), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0, 255), 1)
    
    # Indicador Clip Plane (S)
    if config.clip_plane_enabled:
        axis_names = ["X", "Y", "Z"]
        axis = axis_names[config.clip_plane_axis]
        pos = config.clip_plane_position
        cv2.rectangle(img, (350, 120), (530, 155), (0, 0, 200, 200), -1)
        cv2.putText(img, f"CORTE {axis}: {pos:.1f}", (360, 143), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
    
    # Indicador Multi-modelo
    if len(config.loaded_models) > 1:
        total = len(config.loaded_models)
        idx = config.active_model_idx + 1
        cv2.rectangle(img, (540, 120), (640, 155), (40, 40, 40, 200), -1)
        cv2.rectangle(img, (540, 120), (640, 155), (200, 200, 200, 255), 1)
        cv2.putText(img, f"M {idx}/{total}", (550, 143), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
    
    # Flash de Captura de Pantalla
    if now - config.screenshot_feedback_time < 0.5:
        alpha = int(255 * max(0, 1.0 - (now - config.screenshot_feedback_time) / 0.5))
        cv2.rectangle(img, (0, 0), (820, 200), (255, 255, 255, alpha), -1)
        cv2.putText(img, "Captura Guardada!", (250, 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 200, 0, 255), 2)
        
    return img

def get_model_info_texture(win_w, win_h):
    """
    Panel de información del modelo activo.
    """
    if not config.show_model_info:
        return None
    if not config.loaded_models:
        return None
        
    model = config.loaded_models[config.active_model_idx]
    
    img = np.zeros((win_h, win_w, 4), dtype=np.uint8)
    
    # Panel en esquina inferior derecha
    pw, ph = 280, 140
    px = win_w - pw - 10
    py = win_h - ph - 10
    
    cv2.rectangle(img, (px, py), (px + pw, py + ph), (20, 20, 20, 220), -1)
    cv2.rectangle(img, (px, py), (px + pw, py + ph), (0, 200, 255, 255), 1)
    
    cv2.putText(img, "Info Modelo", (px + 10, py + 25), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 200, 255, 255), 1)
    cv2.putText(img, f"Nombre: {model.file_name}", (px + 10, py + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
    cv2.putText(img, f"Vertices: {model.vertex_count:,}", (px + 10, py + 75), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
    cv2.putText(img, f"Triangulos: {model.face_count:,}", (px + 10, py + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
    cv2.putText(img, f"Tamano: {model.file_size_mb:.2f} MB", (px + 10, py + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
    
    return img
