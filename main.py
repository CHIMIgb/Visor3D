import sys
import os
import threading
import time
import glfw
import numpy as np
import cv2
from OpenGL.GL import *
from OpenGL.GLU import *

import config
from camera_tracker import camera_thread_func
from opengl_renderer import *
from input_handlers import drop_callback, key_callback, mouse_button_callback, cursor_position_callback, scroll_callback
from ui_overlay import get_ui_texture, get_model_info_texture

def main():
    if len(sys.argv) > 1:
        from model_loader import load_model
        model = load_model(sys.argv[1])
        if model:
            config.loaded_models.append(model)
            config.active_model_idx = 0
    
    if not glfw.init():
        print("Error: No se pudo inicializar GLFW")
        return
        
    cam_thread = threading.Thread(target=camera_thread_func)
    cam_thread.start()
    
    # Configurar para que inicie maximizada y adaptada a la pantalla
    glfw.window_hint(glfw.MAXIMIZED, glfw.TRUE)
    monitor = glfw.get_primary_monitor()
    video_mode = glfw.get_video_mode(monitor)
    
    window = glfw.create_window(video_mode.size.width, video_mode.size.height, "Visor 3D por Gestos", None, None)
    
    if not window:
        glfw.terminate()
        config.running = False
        cam_thread.join()
        return
        
    glfw.make_context_current(window)
    glfw.swap_interval(1) # Vsync
    
    # Registrar callbacks
    glfw.set_drop_callback(window, drop_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    
    # Crear carpeta de capturas
    os.makedirs("capturas", exist_ok=True)
    
    print("Esperando a la cámara...")
    time.sleep(1)
    
    while not glfw.window_should_close(window) and config.running:
        glfw.poll_events()
        
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        fb_width, fb_height = glfw.get_framebuffer_size(window)
        half_width = fb_width // 2
        
        frame_to_draw = None
        lms_to_draw = None
        with config.frame_lock:
            if config.current_frame is not None:
                frame_to_draw = config.current_frame.copy()
            if config.current_landmarks_normalized is not None:
                lms_to_draw = config.current_landmarks_normalized
                
        texture_id = None
        cam_w, cam_h = 1280, 720
        if frame_to_draw is not None:
            texture_id = create_texture(frame_to_draw)
            cam_h, cam_w = frame_to_draw.shape[:2]
        
        # Obtener modelo activo
        active_model = None
        if config.loaded_models and config.active_model_idx < len(config.loaded_models):
            active_model = config.loaded_models[config.active_model_idx]
            
        if config.view_mode == 0:
            # ====== PANTALLA DIVIDIDA ======
            vx, vy, vw, vh = get_aspect_correct_viewport(0, 0, half_width, fb_height, cam_w, cam_h)
            glViewport(vx, vy, vw, vh)
            if texture_id:
                draw_textured_quad(texture_id)
                texture_id = None
            
            if lms_to_draw:
                draw_skeleton_opengl(lms_to_draw)
                
            glViewport(half_width, 0, half_width, fb_height)
            aspect = half_width / fb_height if fb_height > 0 else 1.0
            if active_model: draw_model(active_model, aspect)
            else: draw_cube(aspect)
            
        elif config.view_mode == 1:
            # ====== HUD 3D ======
            glViewport(0, 0, fb_width, fb_height)
            aspect = fb_width / fb_height if fb_height > 0 else 1.0
            if active_model: draw_model(active_model, aspect)
            else: draw_cube(aspect)
            
            if lms_to_draw:
                vx, vy, vw, vh = get_aspect_correct_viewport(0, 0, fb_width, fb_height, cam_w, cam_h)
                glViewport(vx, vy, vw, vh)
                draw_skeleton_opengl(lms_to_draw)
                
            if texture_id:
                glDeleteTextures([texture_id])
                
        elif config.view_mode == 2:
            # ====== REALIDAD AUMENTADA ======
            vx, vy, vw, vh = get_aspect_correct_viewport(0, 0, fb_width, fb_height, cam_w, cam_h)
            glViewport(vx, vy, vw, vh)
            if texture_id:
                draw_textured_quad(texture_id)
                texture_id = None
                
            if lms_to_draw:
                draw_skeleton_opengl(lms_to_draw)
                
            glClear(GL_DEPTH_BUFFER_BIT)
            glViewport(0, 0, fb_width, fb_height)
            aspect = fb_width / fb_height if fb_height > 0 else 1.0
            if active_model: draw_model(active_model, aspect)
            else: draw_cube(aspect)
            
        # ====== OVERLAY UI ======
        win_w, win_h = glfw.get_window_size(window)
        
        ui_img = get_ui_texture(config.is_loading_model)
        ui_tex = create_texture(ui_img)
        if ui_tex:
            ui_h, ui_w = ui_img.shape[:2]
            glViewport(0, 0, fb_width, fb_height)
            draw_ui_overlay(ui_tex, win_w, win_h, ui_w, ui_h)
            glDeleteTextures([ui_tex])
            
        # ====== INFO DEL MODELO ======
        info_img = get_model_info_texture(win_w, win_h)
        if info_img is not None:
            info_tex = create_texture(info_img)
            if info_tex:
                info_h, info_w = info_img.shape[:2]
                glViewport(0, 0, fb_width, fb_height)
                draw_ui_overlay(info_tex, win_w, win_h, info_w, info_h)
                glDeleteTextures([info_tex])
        
        # ====== CAPTURA DE PANTALLA ======
        if config.take_screenshot:
            config.take_screenshot = False
            try:
                pixels = glReadPixels(0, 0, fb_width, fb_height, GL_RGB, GL_UNSIGNED_BYTE)
                image = np.frombuffer(pixels, dtype=np.uint8).reshape(fb_height, fb_width, 3)
                image = cv2.flip(image, 0)  # Flip vertical
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filepath = f"capturas/captura_{timestamp}.png"
                cv2.imwrite(filepath, image)
                print(f"Captura guardada: {filepath}")
                config.screenshot_feedback_time = time.time()
            except Exception as e:
                print(f"Error al capturar pantalla: {e}")
        
        glfw.swap_buffers(window)
        
    config.running = False
    cam_thread.join()
    glfw.terminate()

if __name__ == "__main__":
    main()
