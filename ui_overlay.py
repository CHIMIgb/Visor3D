import cv2
import numpy as np
import time
import os
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
        cv2.putText(img, "- 2 Indices: Modo", (650, start_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- 2 Dedos (V): Rotar Z", (650, start_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        cv2.putText(img, "- 2 Manos: Reset", (650, start_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200, 255), 1)
        
    return img

def get_explorer_texture(win_w, win_h):
    if not config.is_explorer_open: return None
    
    img = np.zeros((win_h, win_w, 4), dtype=np.uint8)
    
    # Oscurecer el fondo
    cv2.rectangle(img, (0, 0), (win_w, win_h), (0, 0, 0, 180), -1)
    
    # Dibujar ventana del explorador
    panel_w = 600
    panel_h = 400
    px = (win_w - panel_w) // 2
    py = (win_h - panel_h) // 2
    
    cv2.rectangle(img, (px, py), (px + panel_w, py + panel_h), (40, 40, 40, 240), -1)
    cv2.rectangle(img, (px, py), (px + panel_w, py + panel_h), (0, 200, 255, 255), 2)
    
    cv2.putText(img, "Explorador Holografico 3D", (px + 20, py + 40), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255, 255), 1)
    cv2.putText(img, f"Ruta: {config.current_path}", (px + 20, py + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150, 255), 1)
    
    try:
        items = os.listdir(config.current_path)
    except:
        items = []
        
    valid_items = [".."]
    for item in items:
        try:
            full_path = os.path.join(config.current_path, item)
            if os.path.isdir(full_path):
                valid_items.append("[DIR] " + item)
            elif item.lower().endswith(('.obj', '.stl', '.ply', '.glb', '.gltf')):
                valid_items.append(item)
        except:
            pass
            
    item_height = 30
    start_y = py + 100
    
    # Cursor
    # Efecto espejo en el cursor
    cursor_px = int((1.0 - config.cursor_x) * win_w)
    cursor_py = int(config.cursor_y * win_h)
    
    # Auto-scroll
    if px < cursor_px < px + panel_w:
        if py < cursor_py < py + 90:
            config.explorer_scroll_y -= 0.5
        elif py + panel_h - 50 < cursor_py < py + panel_h:
            config.explorer_scroll_y += 0.5
            
    if config.explorer_scroll_y < 0: config.explorer_scroll_y = 0
    max_scroll = max(0, len(valid_items) - 8)
    if config.explorer_scroll_y > max_scroll: config.explorer_scroll_y = max_scroll
    
    idx_start = int(config.explorer_scroll_y)
    
    config.hovered_item = None
    for i, item in enumerate(valid_items[idx_start:idx_start+8]):
        item_y = start_y + i * item_height
        
        is_hovered = (px + 20 < cursor_px < px + panel_w - 20) and (item_y - 20 < cursor_py < item_y + 10)
        
        color = (0, 255, 0, 255) if is_hovered else (200, 200, 200, 255)
        if is_hovered:
            cv2.rectangle(img, (px + 20, item_y - 22), (px + panel_w - 20, item_y + 8), (80, 80, 80, 255), -1)
            config.hovered_item = item
            
        cv2.putText(img, item, (px + 30, item_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
        
    # Dibujar cursor interactivo
    cv2.circle(img, (cursor_px, cursor_py), 6, (0, 0, 255, 255), -1) 
    cv2.circle(img, (cursor_px, cursor_py), 12, (0, 200, 255, 255), 2) 
    
    return img
