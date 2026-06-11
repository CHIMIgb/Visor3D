import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config

def camera_thread_func():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        config.running = False
        return

    # Forzar HD para tener visión periférica sin estirar
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    base_options = python.BaseOptions(model_asset_path='assets/hand_landmarker.task')
    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
    
    try:
        detector = vision.HandLandmarker.create_from_options(options)
    except Exception as e:
        print(f"Error cargando el modelo de MediaPipe: {e}")
        config.running = False
        cap.release()
        return

    with detector:
        while config.running:
            success, image = cap.read()
            if not success:
                time.sleep(0.1)
                continue

            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            detection_result = detector.detect(mp_image)
            
            with config.frame_lock:
                config.current_frame = rgb_image.copy()
                if detection_result and detection_result.hand_landmarks:
                    config.current_landmarks_normalized = []
                    for hl in detection_result.hand_landmarks:
                        config.current_landmarks_normalized.append([(lm.x, lm.y, lm.z) for lm in hl])
                else:
                    config.current_landmarks_normalized = None
            
            time.sleep(0.01)
            
    cap.release()
