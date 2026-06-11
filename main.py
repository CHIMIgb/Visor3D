import sys
import cv2
import mediapipe as mp
import threading
import time
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Variables compartidas entre threads
frame_lock = threading.Lock()
current_frame = None
running = True
loaded_model = None

# Conexiones de la mano para dibujar manualmente
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
]

def draw_landmarks_manual(image, detection_result):
    if not detection_result or not detection_result.hand_landmarks:
        return
    h, w, _ = image.shape
    for hand_landmarks in detection_result.hand_landmarks:
        for connection in HAND_CONNECTIONS:
            start_idx = connection[0]
            end_idx = connection[1]
            start_pt = hand_landmarks[start_idx]
            end_pt = hand_landmarks[end_idx]
            sx, sy = int(start_pt.x * w), int(start_pt.y * h)
            ex, ey = int(end_pt.x * w), int(end_pt.y * h)
            cv2.line(image, (sx, sy), (ex, ey), (0, 255, 0), 2)
        
        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(image, (cx, cy), 4, (0, 0, 255), -1)

def camera_thread_func():
    global current_frame, running
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        running = False
        return

    # Usar la nueva Tasks API de MediaPipe
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    # Configurar el detector usando el modelo descargado
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
    
    try:
        detector = vision.HandLandmarker.create_from_options(options)
    except Exception as e:
        print(f"Error cargando el modelo de MediaPipe: {e}")
        running = False
        cap.release()
        return

    with detector:
        while running:
            success, image = cap.read()
            if not success:
                print("Frame de cámara vacío, ignorando.")
                time.sleep(0.1)
                continue

            # Invertir la imagen horizontalmente para un efecto espejo "selfie"
            image = cv2.flip(image, 1)

            # Convertir a RGB y crear mp.Image
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            # Detección
            detection_result = detector.detect(mp_image)
            
            # Dibujar resultados
            draw_landmarks_manual(rgb_image, detection_result)

            with frame_lock:
                current_frame = rgb_image.copy()
            
            time.sleep(0.01)
            
    cap.release()

def create_texture(image):
    if image is None:
        return None
    
    height, width, channels = image.shape
    image_data = np.frombuffer(image.tobytes(), np.uint8)
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
    
    return texture_id

def draw_textured_quad(texture_id):
    if texture_id is None:
        return
        
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # Desactivar buffer de profundidad para que la imagen de fondo se dibuje correctamente
    glDisable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1.0, 1.0, 1.0)
    
    glBegin(GL_QUADS)
    # MediaPipe entrega coordenadas donde 0,0 es arriba izquierda, 
    # pero OpenGL espera abajo izquierda. Invertimos Y en texcoords.
    glTexCoord2f(0.0, 1.0); glVertex3f(-1.0, -1.0, 0.0)
    glTexCoord2f(1.0, 1.0); glVertex3f( 1.0, -1.0, 0.0)
    glTexCoord2f(1.0, 0.0); glVertex3f( 1.0,  1.0, 0.0)
    glTexCoord2f(0.0, 0.0); glVertex3f(-1.0,  1.0, 0.0)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glDeleteTextures([texture_id])
    glDisable(GL_TEXTURE_2D)

def draw_cube():
    # Habilitar buffer de profundidad para 3D
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0, 0.1, 50.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5.0)
    
    # Rotar el cubo animadamente
    glRotatef(glfw.get_time() * 50.0, 1, 1, 0)
    
    vertices = (
        ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1), (-1, -1, -1),
        ( 1, -1,  1), ( 1,  1,  1), (-1, -1,  1), (-1,  1,  1)
    )
    
    edges = (
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,7), (7,6), (6,4),
        (0,4), (1,5), (2,7), (3,6)
    )
    
    colors = (
        (0.8,0.2,0.2), (0.2,0.8,0.2), (0.2,0.2,0.8), (0.8,0.8,0.2),
        (0.8,0.2,0.8), (0.2,0.8,0.8), (0.9,0.9,0.9), (0.5,0.5,0.5)
    )
    
    surfaces = (
        (0,1,2,3), (3,2,7,6), (6,7,5,4),
        (4,5,1,0), (1,5,7,2), (4,0,3,6)
    )
    
    glBegin(GL_QUADS)
    for i, surface in enumerate(surfaces):
        glColor3fv(colors[i])
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_model(model_data):
    if not model_data:
        return
        
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0, 0.1, 50.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Movemos la cámara hacia atrás (modelo en el origen de tamaño [-1,1])
    glTranslatef(0.0, 0.0, -3.0)
    
    # Rotación continua sobre el eje Y
    glRotatef(glfw.get_time() * 30.0, 0, 1, 0)
    
    # Configuración de luz básica
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
    
    glColor3f(0.8, 0.8, 0.8) # Color base
    
    # Dibujar usando triángulos (Immediate mode para empezar, optimizable a VBO después)
    glBegin(GL_TRIANGLES)
    for face in model_data.faces:
        for vertex_idx in face:
            # Normales
            if model_data.normals is not None and len(model_data.normals) > vertex_idx:
                glNormal3fv(model_data.normals[vertex_idx])
            # Colores de vértice
            if model_data.colors is not None and len(model_data.colors) > vertex_idx:
                glColor3fv(model_data.colors[vertex_idx])
            # Vértice
            glVertex3fv(model_data.vertices[vertex_idx])
    glEnd()
    
    glDisable(GL_LIGHTING)

def drop_callback(window, paths):
    global loaded_model
    from model_loader import load_model
    if paths:
        new_model = load_model(paths[0])
        if new_model:
            loaded_model = new_model

def key_callback(window, key, scancode, action, mods):
    global loaded_model
    if key == glfw.KEY_O and action == glfw.PRESS:
        import tkinter as tk
        from tkinter import filedialog
        from model_loader import load_model
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True) # Asegurar que aparezca sobre la ventana GLFW
        path = filedialog.askopenfilename(
            title="Seleccionar Modelo 3D",
            filetypes=[("Modelos 3D", "*.obj *.stl *.ply *.glb *.gltf"), ("Todos", "*.*")]
        )
        root.destroy()
        
        if path:
            new_model = load_model(path)
            if new_model:
                loaded_model = new_model

def main():
    global running, current_frame, loaded_model
    
    from model_loader import load_model
    
    model_path = sys.argv[1] if len(sys.argv) > 1 else None
    if model_path:
        loaded_model = load_model(model_path)
    
    if not glfw.init():
        print("Error: No se pudo inicializar GLFW")
        return
        
    cam_thread = threading.Thread(target=camera_thread_func)
    cam_thread.start()
    
    # Ventana ancha para split screen
    window_width, window_height = 1280, 480
    window = glfw.create_window(window_width, window_height, "Visor 3D por Gestos - Fase 1", None, None)
    
    if not window:
        glfw.terminate()
        running = False
        cam_thread.join()
        return
        
    glfw.make_context_current(window)
    glfw.swap_interval(1) # Vsync
    
    # Registrar callbacks para interactividad básica (arrastrar y soltar, teclado)
    glfw.set_drop_callback(window, drop_callback)
    glfw.set_key_callback(window, key_callback)
    
    print("Esperando a la cámara...")
    time.sleep(1)
    
    while not glfw.window_should_close(window) and running:
        glfw.poll_events()
        
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        fb_width, fb_height = glfw.get_framebuffer_size(window)
        half_width = fb_width // 2
        
        # ====== VIEWPORT IZQUIERDO: Cámara ======
        glViewport(0, 0, half_width, fb_height)
        
        frame_to_draw = None
        with frame_lock:
            if current_frame is not None:
                frame_to_draw = current_frame.copy()
                
        if frame_to_draw is not None:
            texture_id = create_texture(frame_to_draw)
            draw_textured_quad(texture_id)
            
        # ====== VIEWPORT DERECHO: Cubo 3D / Modelo ======
        glViewport(half_width, 0, half_width, fb_height)
        if loaded_model:
            draw_model(loaded_model)
        else:
            draw_cube()
        
        glfw.swap_buffers(window)
        
    running = False
    cam_thread.join()
    glfw.terminate()

if __name__ == "__main__":
    main()
