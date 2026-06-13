import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config
import gesture_controller

def camera_thread_func():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        config.running = False
        return

    # Forzar HD y mayor framerate
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)

    def result_callback(result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        with config.frame_lock:
            if result and result.hand_landmarks:
                config.current_landmarks_normalized = []
                for hl in result.hand_landmarks:
                    config.current_landmarks_normalized.append([(lm.x, lm.y, lm.z) for lm in hl])
                gesture_controller.process_gestures(config.current_landmarks_normalized)
            else:
                config.current_landmarks_normalized = None
                gesture_controller.process_gestures(None)

    base_options = python.BaseOptions(model_asset_path='assets/hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options, 
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=2,
        result_callback=result_callback
    )
    
    try:
        detector = vision.HandLandmarker.create_from_options(options)
    except Exception as e:
        print(f"Error cargando el modelo de MediaPipe: {e}")
        config.running = False
        cap.release()
        return

    last_timestamp_ms = 0

    with detector:
        while config.running:
            success, image = cap.read()
            if not success:
                time.sleep(0.01)
                continue

            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            with config.frame_lock:
                config.current_frame = rgb_image.copy()

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            timestamp_ms = int(time.time() * 1000)
            
            # Asegurar timestamps estrictamente crecientes para MediaPipe
            if timestamp_ms <= last_timestamp_ms:
                timestamp_ms = last_timestamp_ms + 1
            last_timestamp_ms = timestamp_ms

            try:
                detector.detect_async(mp_image, timestamp_ms)
            except Exception:
                pass
            
    cap.release()
