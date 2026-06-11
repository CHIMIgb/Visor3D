import time
import math
import config

GESTURE_NONE = "NONE"
GESTURE_FIST = "FIST"
GESTURE_OPEN_PALM = "OPEN_PALM"
GESTURE_ZOOM_MODE = "ZOOM_MODE"
GESTURE_THUMBS_UP = "THUMBS_UP"
GESTURE_OK = "OK"
GESTURE_TWO_FINGERS = "TWO_FINGERS"

# Estado interno
last_pinch_dist = None
last_fist_pos = None
last_palm_pos = None
last_two_fingers_pos = None
last_gesture_time = 0

# Filtro Exponencial y Zonas Muertas
SMOOTH_ALPHA = 0.3
DEADZONE = 0.005

smooth_fist_pos = None
smooth_palm_pos = None
smooth_pinch_dist = None
smooth_two_fingers_pos = None

def get_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

def get_finger_states(lms):
    """
    Devuelve un array de booleanos [pulgar, indice, medio, anular, meñique]
    True = Extendido, False = Doblado.
    Es invariante a la rotación porque usa distancias desde la muñeca.
    """
    wrist = lms[0]
    states = []
    
    # Pulgar (tip=4, mcp=2)
    # Comparamos la distancia a la muñeca desde la punta vs el nudillo
    states.append(get_distance(wrist, lms[4]) > get_distance(wrist, lms[2]))
    
    # Indice (tip=8, pip=6)
    states.append(get_distance(wrist, lms[8]) > get_distance(wrist, lms[6]))
    
    # Medio (tip=12, pip=10)
    states.append(get_distance(wrist, lms[12]) > get_distance(wrist, lms[10]))
    
    # Anular (tip=16, pip=14)
    states.append(get_distance(wrist, lms[16]) > get_distance(wrist, lms[14]))
    
    # Meñique (tip=20, pip=18)
    states.append(get_distance(wrist, lms[20]) > get_distance(wrist, lms[18]))
    
    return states

def classify_hand(lms):
    states = get_finger_states(lms)
    thumb, index, middle, ring, pinky = states
    
    # Comprobar si índice y pulgar se tocan (Pinza)
    pinch_dist = get_distance(lms[4], lms[8])
    is_pinching = pinch_dist < 0.05
    
    # 👌 OK Gesture
    if is_pinching and middle and ring and pinky:
        return GESTURE_OK
        
    # 🤏 ZOOM MODE (Pulgar e Índice extendidos, sin tocarse)
    if thumb and index and not is_pinching and not middle and not ring and not pinky:
        return GESTURE_ZOOM_MODE
        
    # ✊ FIST y 👍 THUMBS_UP
    if not index and not middle and not ring and not pinky:
        if not thumb:
            return GESTURE_FIST
        else:
            return GESTURE_THUMBS_UP
            
    # ✌️ TWO_FINGERS
    if not thumb and index and middle and not ring and not pinky:
        return GESTURE_TWO_FINGERS
        
    # ✋ OPEN_PALM (Exigimos al menos los 4 dedos principales extendidos)
    if index and middle and ring and pinky:
        return GESTURE_OPEN_PALM
        
    return GESTURE_NONE

def apply_smoothing(current_val, prev_val, alpha=SMOOTH_ALPHA):
    if prev_val is None:
        return current_val
    if isinstance(current_val, tuple):
        return (
            prev_val[0] + alpha * (current_val[0] - prev_val[0]),
            prev_val[1] + alpha * (current_val[1] - prev_val[1])
        )
    return prev_val + alpha * (current_val - prev_val)

def process_gestures(landmarks_list):
    global last_pinch_dist, last_fist_pos, last_palm_pos, last_two_fingers_pos
    global smooth_fist_pos, smooth_palm_pos, smooth_pinch_dist, smooth_two_fingers_pos
    global last_gesture_time
    
    detected = []
    
    if not landmarks_list:
        smooth_fist_pos = None
        smooth_palm_pos = None
        smooth_pinch_dist = None
        smooth_two_fingers_pos = None
        last_fist_pos = None
        last_palm_pos = None
        last_two_fingers_pos = None
        last_pinch_dist = None
        config.detected_gestures = []
        return
        
    hand_lms = landmarks_list[0]
    gesture = classify_hand(hand_lms)
    detected.append(gesture)
    
    raw_center_x = hand_lms[9][0]
    raw_center_y = hand_lms[9][1]
    
    current_time = time.time()
    
    # ✊ ROTACIÓN X/Y
    if gesture == GESTURE_FIST:
        smooth_fist_pos = apply_smoothing((raw_center_x, raw_center_y), smooth_fist_pos)
        if last_fist_pos is not None:
            dx = smooth_fist_pos[0] - last_fist_pos[0]
            dy = smooth_fist_pos[1] - last_fist_pos[1]
            if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
                config.camera_yaw += dx * 150.0
                config.camera_pitch += dy * 150.0
                if config.camera_pitch > 89.0: config.camera_pitch = 89.0
                if config.camera_pitch < -89.0: config.camera_pitch = -89.0
                last_fist_pos = smooth_fist_pos
        else:
            last_fist_pos = smooth_fist_pos
    else:
        smooth_fist_pos = None
        last_fist_pos = None
        
    # ✌️ ROTACIÓN Z
    if gesture == GESTURE_TWO_FINGERS:
        smooth_two_fingers_pos = apply_smoothing((raw_center_x, raw_center_y), smooth_two_fingers_pos)
        if last_two_fingers_pos is not None:
            dx = smooth_two_fingers_pos[0] - last_two_fingers_pos[0]
            if abs(dx) > DEADZONE:
                config.camera_roll += dx * 150.0
                last_two_fingers_pos = smooth_two_fingers_pos
        else:
            last_two_fingers_pos = smooth_two_fingers_pos
    else:
        smooth_two_fingers_pos = None
        last_two_fingers_pos = None
        
    # ✋ PANORÁMICA
    if gesture == GESTURE_OPEN_PALM:
        smooth_palm_pos = apply_smoothing((raw_center_x, raw_center_y), smooth_palm_pos)
        if last_palm_pos is not None:
            dx = smooth_palm_pos[0] - last_palm_pos[0]
            dy = smooth_palm_pos[1] - last_palm_pos[1]
            if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
                config.camera_pan_x += dx * 5.0
                config.camera_pan_y -= dy * 5.0
                last_palm_pos = smooth_palm_pos
        else:
            last_palm_pos = smooth_palm_pos
    else:
        smooth_palm_pos = None
        last_palm_pos = None
        
    # 🤏 ZOOM
    if gesture == GESTURE_ZOOM_MODE:
        raw_dist = get_distance(hand_lms[4], hand_lms[8])
        smooth_pinch_dist = apply_smoothing(raw_dist, smooth_pinch_dist)
        if last_pinch_dist is not None:
            ddist = smooth_pinch_dist - last_pinch_dist
            if abs(ddist) > (DEADZONE / 2.0):
                config.camera_distance -= ddist * 20.0
                if config.camera_distance < 0.5: config.camera_distance = 0.5
                if config.camera_distance > 50.0: config.camera_distance = 50.0
                last_pinch_dist = smooth_pinch_dist
        else:
            last_pinch_dist = smooth_pinch_dist
    else:
        smooth_pinch_dist = None
        last_pinch_dist = None
        
    # 👍 PULGAR ARRIBA
    if gesture == GESTURE_THUMBS_UP:
        if current_time - last_gesture_time > 1.0:
            config.current_render_mode_idx = (config.current_render_mode_idx + 1) % len(config.render_modes)
            last_gesture_time = current_time
            
    # 👌 OK
    if gesture == GESTURE_OK:
        if current_time - last_gesture_time > 1.0:
            config.camera_pitch = 0.0
            config.camera_yaw = 0.0
            config.camera_roll = 0.0
            config.camera_pan_x = 0.0
            config.camera_pan_y = 0.0
            config.camera_distance = 3.0
            last_gesture_time = current_time
            
    config.detected_gestures = detected
