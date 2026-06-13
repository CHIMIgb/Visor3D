# 🖐️ Visor 3D por Gestos

Aplicación de escritorio en Python que permite cargar, visualizar y manipular múltiples modelos 3D usando gestos de mano detectados por cámara web, además de ofrecer atajos de teclado para controles avanzados (iluminación, planos de sección, y más).

## Características Principales

*   **Interfaz Gestual:** Controla la rotación, panorámica, zoom y cambio de modos únicamente con gestos intuitivos de tus manos.
*   **Vistas Múltiples:** Soporta vista dividida, HUD Holográfico 3D sobre la cámara, y Realidad Aumentada básica.
*   **Controles Avanzados:** Paleta de colores, iluminación dinámica, planos de sección de corte (`Clip Planes`), e información detallada del modelo.
*   **Multi-modelo:** Permite cargar hasta 5 modelos simultáneamente y navegar entre ellos.
*   **Exportación:** Capturas de pantalla integradas con un simple gesto o tecla.
*   **Renderizado de alto rendimiento:** Motor 3D construido con PyOpenGL y GLFW.

## 🤲 Gestos Soportados

| Gesto | Acción |
|---|---|
| ✋ **Palma Abierta** | Mover (Panorámica X/Y) e Inclinar para Rotar |
| ✊ **Puño Cerrado** | Rotar en X/Y (o mover luz si modo Luz activo) |
| ✌️ **Dos Dedos (V)** | Rotar en el eje Z (Roll) |
| 🤏 **Pulgar + Índice** | Zoom (acercar/alejar la distancia de cámara) |
| ☝️☝️ **Dos Índices** | Ciclar modo de renderizado (Solid, Wireframe, Points) |
| ✋✋ **Dos Palmas** | Resetear posición y rotación de cámara |
| ✊✊ **Dos Puños** | Tomar captura de pantalla |
| 🤙 **Llamada / Surf** | Cambiar color del modelo (Pulgar y Meñique) |

## ⌨️ Atajos de Teclado

| Tecla | Acción |
|---|---|
| `O` | Abrir explorador de archivos para cargar un modelo |
| `V` | Ciclar modos de vista (Dividida / HUD / AR) |
| `M` | Ciclar modo de renderizado |
| `G` | Activar/desactivar la cuadrícula (Grid) del suelo |
| `C` | Ciclar color del modelo (Gris, Rojo, Verde, Azul...) |
| `L` | Alternar modo de iluminación dinámica |
| `S` | Activar/desactivar sección de corte (Clip Plane) |
| `X` | Cambiar eje de corte (X, Y, Z) (cuando `S` activo) |
| `Scroll` | Mover el plano de corte (cuando `S` activo) |
| `I` | Mostrar panel de información del modelo |
| `←` / `→` | Navegar entre modelos cargados (máx 5) |
| `Delete` | Eliminar el modelo activo de la memoria |
| `P` | Tomar captura de pantalla |

## Instalación

1.  Clona el repositorio:
    ```bash
    git clone https://github.com/tu-usuario/Visor3D.git
    cd Visor3D
    ```

2.  Crea y activa un entorno virtual:
    *   **Windows (PowerShell):**
        ```powershell
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Con el entorno virtual activado, ejecuta el script principal:

```bash
python main.py [ruta_al_modelo.obj]
```

Puedes iniciar la aplicación cargando un modelo por defecto pasándole la ruta como argumento, o simplemente iniciar `main.py` y arrastrar y soltar (Drag & Drop) un modelo `.obj`, `.stl`, o `.ply` a la ventana.

## Dependencias

*   `opencv-python`
*   `mediapipe`
*   `PyOpenGL`
*   `glfw`
*   `numpy`
*   `trimesh` & `open3d` (Para carga de modelos)
