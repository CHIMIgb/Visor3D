import threading
import os

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
show_gestures_menu = False

# Fase 6: UI Explorer
is_explorer_open = False
current_path = os.getcwd()
recent_files = []
cursor_x = 0.5
cursor_y = 0.5
explorer_scroll_y = 0.0
hovered_item = None
window_width = 800
window_height = 600

# Para control con ratón
is_mouse_dragging = False
last_mouse_x = 0
last_mouse_y = 0
