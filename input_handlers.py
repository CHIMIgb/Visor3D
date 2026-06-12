import glfw
import threading
import config
import os
from model_loader import load_model

def start_loading_model(path):
    def load_task():
        config.is_loading_model = True
        try:
            print("Cargando modelo en segundo plano, por favor espera...")
            new_model = load_model(path)
            if new_model:
                config.loaded_model = new_model
        finally:
            config.is_loading_model = False
            
    threading.Thread(target=load_task).start()

def drop_callback(window, paths):
    if not paths: return
    start_loading_model(paths[0])

def open_file_dialog():
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    path = filedialog.askopenfilename(
        title="Seleccionar Modelo 3D",
        filetypes=[("Modelos 3D", "*.obj *.stl *.ply *.glb *.gltf"), ("Todos", "*.*")]
    )
    root.destroy()
    
    if path:
        start_loading_model(path)

def key_callback(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_O:
            threading.Thread(target=open_file_dialog).start()
        elif key == glfw.KEY_V:
            config.view_mode = (config.view_mode + 1) % 3
        elif key == glfw.KEY_M:
            config.current_render_mode_idx = (config.current_render_mode_idx + 1) % len(config.render_modes)
        elif key == glfw.KEY_G:
            config.show_grid = not config.show_grid

def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT:
        xpos, ypos = glfw.get_cursor_pos(window)
        
        if action == glfw.PRESS:
            # Primero chequear si hizo clic en los botones de la UI (arriba a la izquierda)
            if 10 <= ypos <= 40:
                if 10 <= xpos <= 160:
                    threading.Thread(target=open_file_dialog).start()
                    return
                elif 170 <= xpos <= 320:
                    config.view_mode = (config.view_mode + 1) % 3
                    return
                elif 330 <= xpos <= 480:
                    config.current_render_mode_idx = (config.current_render_mode_idx + 1) % len(config.render_modes)
                    return
                elif 490 <= xpos <= 640:
                    config.show_grid = not config.show_grid
                    return
                elif 650 <= xpos <= 800:
                    config.show_gestures_menu = not config.show_gestures_menu
                    return
            
            # Si no hizo clic en la UI, iniciar rotación orbital
            config.is_mouse_dragging = True
            config.last_mouse_x = xpos
            config.last_mouse_y = ypos
            
        elif action == glfw.RELEASE:
            config.is_mouse_dragging = False

def cursor_position_callback(window, xpos, ypos):
    if config.is_mouse_dragging:
        dx = xpos - config.last_mouse_x
        dy = ypos - config.last_mouse_y
        
        config.camera_yaw += dx * 0.5
        config.camera_pitch += dy * 0.5
        
        # Limitar el pitch para no dar la vuelta completa por arriba/abajo
        if config.camera_pitch > 89.0: config.camera_pitch = 89.0
        if config.camera_pitch < -89.0: config.camera_pitch = -89.0
        
        config.last_mouse_x = xpos
        config.last_mouse_y = ypos

def scroll_callback(window, xoffset, yoffset):
    config.camera_distance -= yoffset * 0.5
    if config.camera_distance < 0.5: config.camera_distance = 0.5
    if config.camera_distance > 50.0: config.camera_distance = 50.0

def handle_gesture_click(cursor_x, cursor_y):
    # Convertir (0-1) a coordenadas de pantalla (espejado)
    win_w = config.window_width
    win_h = config.window_height
    xpos = (1.0 - cursor_x) * win_w
    ypos = cursor_y * win_h
    
    if not config.is_explorer_open:
        # Chequear click en botones superiores
        if 10 <= ypos <= 40:
            if 10 <= xpos <= 160:
                config.is_explorer_open = True
                return
            elif 170 <= xpos <= 320:
                config.view_mode = (config.view_mode + 1) % 3
                return
            elif 330 <= xpos <= 480:
                config.current_render_mode_idx = (config.current_render_mode_idx + 1) % len(config.render_modes)
                return
            elif 490 <= xpos <= 640:
                config.show_grid = not config.show_grid
                return
            elif 650 <= xpos <= 800:
                config.show_gestures_menu = not config.show_gestures_menu
                return
    else:
        # Explorador abierto
        panel_w = 600
        panel_h = 400
        px = (win_w - panel_w) // 2
        py = (win_h - panel_h) // 2
        
        if px < xpos < px + panel_w and py < ypos < py + panel_h:
            # Click dentro del panel
            if config.hovered_item:
                item = config.hovered_item
                if item == "..":
                    config.current_path = os.path.dirname(config.current_path)
                    config.explorer_scroll_y = 0
                elif item.startswith("[DIR] "):
                    config.current_path = os.path.join(config.current_path, item[6:])
                    config.explorer_scroll_y = 0
                else:
                    path = os.path.join(config.current_path, item)
                    config.is_explorer_open = False
                    start_loading_model(path)
        else:
            # Click fuera, cerrar explorador
            config.is_explorer_open = False
