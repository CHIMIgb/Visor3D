import glfw
import threading
import time
import config
from model_loader import load_model

def start_loading_model(path):
    def load_task():
        config.is_loading_model = True
        try:
            print("Cargando modelo en segundo plano, por favor espera...")
            new_model = load_model(path)
            if new_model:
                # Multi-modelo: añadir a la lista (máx 5)
                if len(config.loaded_models) >= 5:
                    config.loaded_models[config.active_model_idx] = new_model
                else:
                    config.loaded_models.append(new_model)
                    config.active_model_idx = len(config.loaded_models) - 1
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
        # Fase 7: Nuevos atajos
        elif key == glfw.KEY_C:
            config.current_color_idx = (config.current_color_idx + 1) % len(config.color_palette)
            config.color_feedback_time = time.time()
        elif key == glfw.KEY_L:
            config.light_mode = not config.light_mode
        elif key == glfw.KEY_S:
            config.clip_plane_enabled = not config.clip_plane_enabled
        elif key == glfw.KEY_X:
            if config.clip_plane_enabled:
                config.clip_plane_axis = (config.clip_plane_axis + 1) % 3
        elif key == glfw.KEY_I:
            config.show_model_info = not config.show_model_info
        elif key == glfw.KEY_P:
            config.take_screenshot = True
        elif key == glfw.KEY_LEFT:
            if len(config.loaded_models) > 1:
                config.active_model_idx = (config.active_model_idx - 1) % len(config.loaded_models)
        elif key == glfw.KEY_RIGHT:
            if len(config.loaded_models) > 1:
                config.active_model_idx = (config.active_model_idx + 1) % len(config.loaded_models)
        elif key == glfw.KEY_DELETE:
            if len(config.loaded_models) > 0:
                # Invalidar display list antes de borrar
                model = config.loaded_models[config.active_model_idx]
                if hasattr(model, 'display_list_id'):
                    from OpenGL.GL import glDeleteLists
                    try:
                        glDeleteLists(model.display_list_id, 1)
                    except:
                        pass
                config.loaded_models.pop(config.active_model_idx)
                if config.active_model_idx >= len(config.loaded_models) and len(config.loaded_models) > 0:
                    config.active_model_idx = len(config.loaded_models) - 1
                elif len(config.loaded_models) == 0:
                    config.active_model_idx = 0

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
        
        if config.light_mode:
            config.light_yaw += dx * 0.02
            config.light_pitch += dy * 0.02
            if config.light_pitch > 1.5: config.light_pitch = 1.5
            if config.light_pitch < -1.5: config.light_pitch = -1.5
        else:
            config.camera_yaw += dx * 0.5
            config.camera_pitch += dy * 0.5
            if config.camera_pitch > 89.0: config.camera_pitch = 89.0
            if config.camera_pitch < -89.0: config.camera_pitch = -89.0
        
        config.last_mouse_x = xpos
        config.last_mouse_y = ypos

def scroll_callback(window, xoffset, yoffset):
    if config.clip_plane_enabled:
        config.clip_plane_position += yoffset * 0.1
        if config.clip_plane_position < -2.0: config.clip_plane_position = -2.0
        if config.clip_plane_position > 2.0: config.clip_plane_position = 2.0
    else:
        config.camera_distance -= yoffset * 0.5
        if config.camera_distance < 0.5: config.camera_distance = 0.5
        if config.camera_distance > 50.0: config.camera_distance = 50.0
