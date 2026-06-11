import os
import numpy as np

class ModelData:
    def __init__(self, vertices, faces, normals=None, colors=None):
        self.vertices = vertices
        self.faces = faces
        self.normals = normals
        self.colors = colors

def normalize_model(vertices):
    """
    Centra el modelo en (0,0,0) y lo escala para que quepa en un cubo de [-1, 1]
    """
    if len(vertices) == 0:
        return vertices
        
    # Calcular bounding box
    min_bounds = np.min(vertices, axis=0)
    max_bounds = np.max(vertices, axis=0)
    center = (min_bounds + max_bounds) / 2.0
    
    # Centrar
    centered_vertices = vertices - center
    
    # Escalar
    max_range = np.max(max_bounds - min_bounds)
    if max_range > 0:
        # Queremos que el rango máximo sea 2 (de -1 a 1), así que dividimos por max_range/2
        scale_factor = 2.0 / max_range
        scaled_vertices = centered_vertices * scale_factor
    else:
        scaled_vertices = centered_vertices
        
    return scaled_vertices

def load_with_open3d(path):
    import open3d as o3d
    
    mesh = o3d.io.read_triangle_mesh(path)
    if not mesh.has_vertices():
        return None
        
    # Asegurar que tengamos triángulos
    if not mesh.has_triangles():
        return None
        
    # Computar normales si no existen
    if not mesh.has_vertex_normals():
        mesh.compute_vertex_normals()
        
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.triangles)
    normals = np.asarray(mesh.vertex_normals)
    
    # Extraer colores de vértices si están disponibles
    colors = None
    if mesh.has_vertex_colors():
        colors = np.asarray(mesh.vertex_colors)
        
    return ModelData(vertices, faces, normals, colors)

def load_with_trimesh(path):
    import trimesh
    
    # Trimesh puede cargar escenas (múltiples mallas). Las combinamos en una sola.
    scene_or_mesh = trimesh.load(path, force='mesh')
    
    if isinstance(scene_or_mesh, trimesh.Scene):
        if len(scene_or_mesh.geometry) == 0:
            return None
        mesh = trimesh.util.concatenate(
            tuple(trimesh.Trimesh(vertices=g.vertices, faces=g.faces) 
                  for g in scene_or_mesh.geometry.values())
        )
    else:
        mesh = scene_or_mesh
        
    vertices = np.array(mesh.vertices)
    faces = np.array(mesh.faces)
    
    # Trimesh computa normales automáticamente
    normals = np.array(mesh.vertex_normals)
    
    # Manejo de colores básicos
    colors = None
    if hasattr(mesh.visual, 'vertex_colors') and len(mesh.visual.vertex_colors) == len(vertices):
        # trimesh colors are usually RGBA 0-255, we need RGB 0.0-1.0
        colors = mesh.visual.vertex_colors[:, :3] / 255.0
        
    return ModelData(vertices, faces, normals, colors)

def load_model(path):
    """
    Función principal para cargar un modelo 3D usando Open3D como primario
    y Trimesh como secundario/fallback.
    """
    if not os.path.exists(path):
        print(f"Error: El archivo {path} no existe.")
        return None
        
    print(f"Cargando modelo: {path}")
    
    model_data = None
    
    # 1. Intentar con Open3D
    try:
        model_data = load_with_open3d(path)
        if model_data is not None:
            print("Modelo cargado exitosamente con Open3D.")
    except Exception as e:
        print(f"Open3D falló al cargar el modelo: {e}")
        
    # 2. Intentar con Trimesh si Open3D falló
    if model_data is None:
        try:
            print("Intentando cargar con Trimesh (fallback)...")
            model_data = load_with_trimesh(path)
            if model_data is not None:
                print("Modelo cargado exitosamente con Trimesh.")
        except Exception as e:
            print(f"Trimesh falló al cargar el modelo: {e}")
            
    # 3. pyassimp podría ser añadido aquí para formatos muy específicos como .fbx si es requerido
    
    # Si todo falló
    if model_data is None:
        print("Error: Ningún cargador pudo procesar el archivo.")
        return None
        
    # Aplicar Normalización (Centrado y Escalado)
    print("Normalizando geometría (centrado y escalado)...")
    model_data.vertices = normalize_model(model_data.vertices)
    
    print(f"Modelo listo: {len(model_data.vertices)} vértices, {len(model_data.faces)} caras.")
    return model_data
