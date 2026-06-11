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

# Configuración de MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def camera_thread_func():
    global current_frame, running
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        running = False
        return

    # Inicializar detección de manos
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        
        while running:
            success, image = cap.read()
            if not success:
                print("Frame de cámara vacío, ignorando.")
                time.sleep(0.1)
                continue

            # Convertir imagen para MediaPipe (de BGR a RGB)
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            # Dibujar landmarks
            image.flags.writeable = True
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

            # Actualizar frame de forma segura
            with frame_lock:
                current_frame = image.copy()
            
            # Pequeño sleep para evitar uso excesivo de CPU
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

def main():
    global running, current_frame
    
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
            
        # ====== VIEWPORT DERECHO: Cubo 3D ======
        glViewport(half_width, 0, half_width, fb_height)
        draw_cube()
        
        glfw.swap_buffers(window)
        
    running = False
    cam_thread.join()
    glfw.terminate()

if __name__ == "__main__":
    main()
