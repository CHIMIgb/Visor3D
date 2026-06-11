import threading

# Variables globales compartidas entre hilos y módulos
frame_lock = threading.Lock()
current_frame = None
current_landmarks_normalized = None

running = True
loaded_model = None
is_loading_model = False
view_mode = 0  # 0: Dividida, 1: HUD 3D, 2: Realidad Aumentada
