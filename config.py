import threading

# Variables globales compartidas entre hilos y módulos
frame_lock = threading.Lock()
current_frame = None
current_landmarks_normalized = None

running = True
loaded_model = None
is_loading_model = False
view_mode = 0  # 0: Dividida, 1: HUD 3D, 2: Realidad Aumentada

# Fase 3: Renderizado Avanzado
render_modes = ["SOLID", "WIREFRAME", "SOLID+WIRE", "POINTS"]
current_render_mode_idx = 0
show_grid = True

# Fase 3/4/5: Cámara Orbital y Panorámica
camera_distance = 3.0
camera_yaw = 0.0
camera_pitch = 0.0
camera_roll = 0.0
camera_pan_x = 0.0
camera_pan_y = 0.0

# Fase 4: Gestos
detected_gestures = []

# Para control con ratón
is_mouse_dragging = False
last_mouse_x = 0
last_mouse_y = 0
