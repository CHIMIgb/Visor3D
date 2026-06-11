import glfw
import threading
import config
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

def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        xpos, ypos = glfw.get_cursor_pos(window)
        # UI is drawn exactly at top left, scale 1:1 with window coordinates.
        if 10 <= xpos <= 160 and 10 <= ypos <= 40:
            threading.Thread(target=open_file_dialog).start()
        elif 170 <= xpos <= 320 and 10 <= ypos <= 40:
            config.view_mode = (config.view_mode + 1) % 3
