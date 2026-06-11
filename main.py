import sys
import threading
import time
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

import config
from camera_tracker import camera_thread_func
from opengl_renderer import *
from input_handlers import drop_callback, key_callback, mouse_button_callback
from ui_overlay import get_ui_texture

def main():
    if len(sys.argv) > 1:
        from model_loader import load_model
        config.loaded_model = load_model(sys.argv[1])
    
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
            
        if config.view_mode == 0:
            # ====== PANTALLA DIVIDIDA ======
            vx, vy, vw, vh = get_aspect_correct_viewport(0, 0, half_width, fb_height, cam_w, cam_h)
            glViewport(vx, vy, vw, vh)
            if texture_id:
                draw_textured_quad(texture_id)
                texture_id = None
                
            glViewport(half_width, 0, half_width, fb_height)
            aspect = half_width / fb_height if fb_height > 0 else 1.0
            if config.loaded_model: draw_model(config.loaded_model, aspect)
            else: draw_cube(aspect)
            
        elif config.view_mode == 1:
            # ====== HUD 3D ======
            glViewport(0, 0, fb_width, fb_height)
            aspect = fb_width / fb_height if fb_height > 0 else 1.0
            if config.loaded_model: draw_model(config.loaded_model, aspect)
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
                
            glClear(GL_DEPTH_BUFFER_BIT)
            glViewport(0, 0, fb_width, fb_height)
            aspect = fb_width / fb_height if fb_height > 0 else 1.0
            if config.loaded_model: draw_model(config.loaded_model, aspect)
            else: draw_cube(aspect)
            
        # ====== OVERLAY UI ======
        ui_img = get_ui_texture(config.is_loading_model)
        ui_tex = create_texture(ui_img)
        if ui_tex:
            ui_h, ui_w = ui_img.shape[:2]
            glViewport(0, 0, fb_width, fb_height)
            win_w, win_h = glfw.get_window_size(window)
            draw_ui_overlay(ui_tex, win_w, win_h, ui_w, ui_h)
            glDeleteTextures([ui_tex])
        
        glfw.swap_buffers(window)
        
    config.running = False
    cam_thread.join()
    glfw.terminate()

if __name__ == "__main__":
    main()
