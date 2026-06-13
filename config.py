import threading

# Variables globales compartidas entre hilos y módulos
frame_lock = threading.Lock()
current_frame = None
current_landmarks_normalized = None

running = True
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
show_gestures_menu = False

# Para control con ratón
is_mouse_dragging = False
last_mouse_x = 0
last_mouse_y = 0

# Fase 5: Multi-Modelo
loaded_models = []  # Lista de ModelData (máx 5)
active_model_idx = 0

# Fase 7: Paleta de Colores
color_palette = [
    (0.8, 0.8, 0.8),   # Gris (default)
    (0.9, 0.2, 0.2),   # Rojo
    (0.2, 0.8, 0.2),   # Verde
    (0.2, 0.4, 0.9),   # Azul
    (0.9, 0.9, 0.2),   # Amarillo
    (0.2, 0.9, 0.9),   # Cian
    (0.9, 0.2, 0.9),   # Magenta
    (1.0, 0.5, 0.0),   # Naranja
]
color_names = ["Gris", "Rojo", "Verde", "Azul", "Amarillo", "Cian", "Magenta", "Naranja"]
current_color_idx = 0
color_feedback_time = 0.0

# Fase 7: Iluminación Dinámica
light_mode = False
light_yaw = 0.785  # ~45 grados
light_pitch = 0.785

# Fase 7: Secciones (Clip Plane)
clip_plane_enabled = False
clip_plane_position = 0.0  # -2.0 a 2.0
clip_plane_axis = 0  # 0=X, 1=Y, 2=Z

# Fase 7: Info del Modelo
show_model_info = False

# Fase 7: Captura de Pantalla
take_screenshot = False
screenshot_feedback_time = 0.0
