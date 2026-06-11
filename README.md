# 🖐️ Visor 3D por Gestos

Aplicación de escritorio en Python que permite cargar, visualizar y manipular modelos 3D de cualquier formato usando únicamente gestos de mano detectados por cámara web, sin necesidad de mouse ni teclado.

## Características Principales

*   **Interfaz gestual:** Controla la rotación, zoom y manipulación de los modelos únicamente con el movimiento de tus manos.
*   **Detección en tiempo real:** Uso de MediaPipe y OpenCV para un reconocimiento de gestos fluido y preciso.
*   **Renderizado de alto rendimiento:** Motor 3D construido con PyOpenGL y GLFW para visualización eficiente.

## Requisitos del Sistema

*   Python 3.8+
*   Cámara web funcional

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
python main.py
```

Se abrirá una ventana mostrando la cámara a la izquierda con el reconocimiento de tus manos, y un entorno 3D de prueba (un cubo giratorio) a la derecha.

## Dependencias

*   `opencv-python`
*   `mediapipe`
*   `PyOpenGL`
*   `glfw`
*   `numpy`

## Estructura del Proyecto

*   `main.py`: Script de entrada de la aplicación.
*   `visor3D_gestos.md`: Documentación interna y diseño del proyecto.
*   `requirements.txt`: Lista de dependencias.
