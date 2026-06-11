import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import config

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
]

def create_texture(image):
    if image is None: return None
    height, width, channels = image.shape
    image_data = np.frombuffer(image.tobytes(), np.uint8)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    format_gl = GL_RGBA if channels == 4 else GL_RGB
    glTexImage2D(GL_TEXTURE_2D, 0, format_gl, width, height, 0, format_gl, GL_UNSIGNED_BYTE, image_data)
    return texture_id

def draw_ui_overlay(texture_id, win_w, win_h, img_w, img_h):
    if texture_id is None or win_w == 0 or win_h == 0: return
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, win_w, win_h, 0, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex2f(0, 0)
    glTexCoord2f(1.0, 0.0); glVertex2f(img_w, 0)
    glTexCoord2f(1.0, 1.0); glVertex2f(img_w, img_h)
    glTexCoord2f(0.0, 1.0); glVertex2f(0, img_h)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)

def draw_textured_quad(texture_id):
    if texture_id is None: return
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
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
    glEnable(GL_DEPTH_TEST)

def draw_grid():
    if not config.show_grid: return
    glDisable(GL_LIGHTING)
    glColor3f(0.4, 0.4, 0.4)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    # Rejilla en el suelo (y = -1.0)
    for i in range(-5, 6):
        glVertex3f(i, -1.0, -5)
        glVertex3f(i, -1.0, 5)
        glVertex3f(-5, -1.0, i)
        glVertex3f(5, -1.0, i)
    glEnd()

def apply_camera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -config.camera_distance)
    glRotatef(config.camera_pitch, 1, 0, 0)
    glRotatef(config.camera_yaw, 0, 1, 0)

def set_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Phong Lighting Components
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    # Luz direccional desde arriba y derecha
    glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
    
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 64.0)
    
    # Asegurar que las normales sean unitarias tras escalar
    glEnable(GL_NORMALIZE)

def execute_render_mode(render_func):
    mode = config.render_modes[config.current_render_mode_idx]
    
    if mode == "SOLID":
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        set_lighting()
        render_func()
        glDisable(GL_LIGHTING)
        
    elif mode == "WIREFRAME":
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 1.0, 0.0) # Verde
        render_func()
        
    elif mode == "SOLID+WIRE":
        # Draw solid
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        set_lighting()
        render_func()
        glDisable(GL_LIGHTING)
        glDisable(GL_POLYGON_OFFSET_FILL)
        
        # Draw wireframe on top
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(0.0, 0.0, 0.0) # Negro
        render_func()
        
    elif mode == "POINTS":
        glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
        glPointSize(4.0)
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 0.5, 0.0) # Naranja
        render_func()
        
    # Reset
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

def render_cube_geometry():
    vertices = ((1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,-1),(1,-1,1),(1,1,1),(-1,-1,1),(-1,1,1))
    edges = ((0,1),(1,2),(2,3),(3,0),(4,5),(5,7),(7,6),(6,4),(0,4),(1,5),(2,7),(3,6))
    colors = ((0.8,0.2,0.2),(0.2,0.8,0.2),(0.2,0.2,0.8),(0.8,0.8,0.2),(0.8,0.2,0.8),(0.2,0.8,0.8),(0.9,0.9,0.9),(0.5,0.5,0.5))
    surfaces = ((0,1,2,3),(3,2,7,6),(6,7,5,4),(4,5,1,0),(1,5,7,2),(4,0,3,6))
    
    # Calcular normales de las caras del cubo para la iluminación
    glBegin(GL_QUADS)
    for i, surface in enumerate(surfaces):
        glColor3fv(colors[i])
        # Normal rudimentaria para el cubo basado en sus vértices
        v1 = np.array(vertices[surface[0]])
        v2 = np.array(vertices[surface[1]])
        v3 = np.array(vertices[surface[2]])
        normal = np.cross(v2 - v1, v3 - v1)
        norm = np.linalg.norm(normal)
        if norm > 0: normal = normal / norm
        glNormal3fv(normal)
        
        for vertex in surface: 
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_cube(aspect_ratio):
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, aspect_ratio, 0.1, 50.0)
    apply_camera()
    draw_grid()
    execute_render_mode(render_cube_geometry)

def render_model_geometry(model_data):
    glColor3f(0.8, 0.8, 0.8)
    if not hasattr(model_data, 'display_list_id'):
        model_data.display_list_id = glGenLists(1)
        glNewList(model_data.display_list_id, GL_COMPILE)
        glBegin(GL_TRIANGLES)
        for face in model_data.faces:
            for vertex_idx in face:
                if model_data.normals is not None and len(model_data.normals) > vertex_idx:
                    glNormal3fv(model_data.normals[vertex_idx])
                if model_data.colors is not None and len(model_data.colors) > vertex_idx:
                    glColor3fv(model_data.colors[vertex_idx])
                glVertex3fv(model_data.vertices[vertex_idx])
        glEnd()
        glEndList()
    glCallList(model_data.display_list_id)

def draw_model(model_data, aspect_ratio):
    if not model_data: return
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, aspect_ratio, 0.1, 50.0)
    apply_camera()
    draw_grid()
    execute_render_mode(lambda: render_model_geometry(model_data))

def draw_skeleton_opengl(landmarks_list):
    if not landmarks_list: return
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0.0, 1.0, 1.0, 0.0, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glLineWidth(3.0)
    for hand_lms in landmarks_list:
        glColor3f(0.0, 0.8, 0.0)
        glBegin(GL_LINES)
        for connection in HAND_CONNECTIONS:
            p1, p2 = hand_lms[connection[0]], hand_lms[connection[1]]
            glVertex2f(p1[0], p1[1])
            glVertex2f(p2[0], p2[1])
        glEnd()
        glPointSize(8.0)
        glColor3f(1.0, 0.2, 0.2)
        glBegin(GL_POINTS)
        for p in hand_lms: glVertex2f(p[0], p[1])
        glEnd()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)

def get_aspect_correct_viewport(x, y, w, h, img_w, img_h):
    if h == 0 or img_h == 0: return x, y, w, h
    view_aspect = w / h
    img_aspect = img_w / img_h
    if view_aspect > img_aspect:
        new_w = int(h * img_aspect)
        new_h = h
        new_x = x + (w - new_w) // 2
        new_y = y
    else:
        new_w = w
        new_h = int(w / img_aspect)
        new_x = x
        new_y = y + (h - new_h) // 2
    return new_x, new_y, new_w, new_h
