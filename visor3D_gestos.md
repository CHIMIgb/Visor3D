# 🖐️ Visor 3D por Gestos — Documentación del Proyecto

> Aplicación de escritorio que permite cargar, visualizar y manipular modelos 3D de cualquier formato usando únicamente gestos de mano detectados por cámara web, sin necesidad de mouse ni teclado.

---

## 🧭 Visión General

| Atributo | Detalle |
|---|---|
| **Tipo** | Aplicación de escritorio (Python) |
| **Interfaz de usuario** | Gestos de mano (sin mouse/teclado) |
| **Detección de movimiento** | MediaPipe Hands + OpenCV |
| **Renderizado 3D** | PyOpenGL + GLFW |
| **Carga de modelos** | Open3D + Trimesh (soporte universal) |
| **Formatos soportados** | `.obj`, `.fbx`, `.glb`, `.gltf`, `.stl`, `.ply`, `.dae`, `.3ds`, `.blend`, `.usd`, y más |

---

## 📐 Arquitectura General

```
┌─────────────────────────────────────────────────────┐
│                   APLICACIÓN PRINCIPAL               │
│                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌────────┐ │
│  │  Módulo de   │    │  Módulo de   │    │  UI    │ │
│  │  Detección   │───▶│  Gestos      │───▶│  3D    │ │
│  │  (OpenCV +   │    │  (Lógica de  │    │  (OGL) │ │
│  │  MediaPipe)  │    │  comandos)   │    │        │ │
│  └──────────────┘    └──────────────┘    └────────┘ │
│                                               │      │
│                          ┌────────────────────┘      │
│                          ▼                           │
│                  ┌───────────────┐                   │
│                  │  Motor de     │                   │
│                  │  Modelos 3D   │                   │
│                  │  (Open3D /    │                   │
│                  │   Trimesh)    │                   │
│                  └───────────────┘                   │
└─────────────────────────────────────────────────────┘
```

---

## 🗂️ Fases de Implementación

---

### ✅ Fase 1 — Infraestructura Base

**Objetivo:** Tener el entorno funcionando con cámara activa y ventana 3D abierta en paralelo.

**Duración estimada:** 1–2 semanas

#### Tareas

- [ ] Configurar entorno virtual Python (`venv` o `conda`)
- [ ] Instalar dependencias base: `opencv-python`, `mediapipe`, `PyOpenGL`, `glfw`, `numpy`
- [ ] Captura de video en tiempo real con OpenCV
- [ ] Ventana GLFW con contexto OpenGL activo
- [ ] Bucle principal que actualiza cámara y renderizado en threads separados
- [ ] Mostrar feed de cámara con landmarks de mano superpuestos (debug visual)

#### Stack

```
opencv-python
mediapipe
PyOpenGL
glfw
numpy
```

#### Entregable
> Ventana dividida: cámara con puntos de mano detectados a la izquierda, cubo 3D básico renderizado a la derecha.

---

### ✅ Fase 2 — Carga Universal de Modelos 3D

**Objetivo:** Soporte para cualquier formato 3D disponible en el mercado.

**Duración estimada:** 1–2 semanas

#### Formatos soportados

| Categoría | Formatos |
|---|---|
| Estándar abierto | `.obj`, `.stl`, `.ply`, `.gltf`, `.glb` |
| Software comercial | `.fbx`, `.dae` (Collada), `.3ds`, `.blend` |
| CAD / Ingeniería | `.step`, `.iges`, `.usd`, `.usda` |
| Punto de nube | `.pcd`, `.xyz`, `.pts` |

#### Tareas

- [ ] Integrar `Open3D` como lector primario (soporta la mayoría de formatos)
- [ ] Integrar `Trimesh` como lector secundario/respaldo
- [ ] Pipeline de normalización: centrar modelo, escalar a tamaño estándar
- [ ] Conversión interna a estructura unificada: `vertices`, `faces`, `normals`, `uvs`
- [ ] Manejo de errores para formatos no soportados o archivos corruptos
- [ ] Gestión de modelos con múltiples meshes / submateriales

#### Librería principal

```
open3d
trimesh
pyassimp   # para .fbx, .dae, .blend
```

#### Entregable
> Función `load_model(path)` que acepta cualquier archivo 3D y devuelve una estructura renderizable.

---

### ✅ Fase 3 — Renderizado 3D Avanzado

**Objetivo:** Visor 3D completo con iluminación, materiales y modos de visualización.

**Duración estimada:** 2–3 semanas

#### Tareas

- [ ] Renderizado de malla (wireframe) y sólido (shaded)
- [ ] Iluminación Phong básica (ambiental + difusa + especular)
- [ ] Cámara orbital con matrices de transformación (modelo-vista-proyección)
- [ ] Buffer de profundidad (Z-buffer) para visibilidad correcta
- [ ] Normales por vértice o por cara (smooth/flat shading)
- [ ] Sistema de colores por vértice o material uniforme
- [ ] Grid de referencia en el suelo (opcional, toggle)
- [ ] Soporte para modelos con texturas básicas (UV mapping)

#### Modos de visualización

```
SOLID       → renderizado lleno con iluminación
WIREFRAME   → solo aristas de la malla
SOLID+WIRE  → combinado (X-Ray look)
POINTS      → solo vértices (para nubes de puntos)
```

#### Entregable
> Cualquier modelo 3D cargado se ve correctamente en los 4 modos con iluminación básica.

---

### ✅ Fase 4 — Diccionario de Gestos

**Objetivo:** Definir y reconocer los gestos que controlan la aplicación.

**Duración estimada:** 2 semanas

#### Gestos definidos

| Gesto | Acción | Descripción |
|---|---|---|
| ✊ Puño cerrado + arrastrar | Rotar modelo | Cerrar puño y mover la mano |
| 🤏 Pinza con dos manos | Zoom | Alejar/acercar los dedos índice-pulgar |
| ✋ Palma abierta + arrastrar | Mover modelo (pan) | Mano abierta y desplazar |
| ☝️ Índice apuntando | Seleccionar en menú | Cursor gestual |
| 👌 OK (círculo) | Confirmar selección | Índice + pulgar forman círculo |
| ✌️ Dos dedos + girar | Rotar en Z | Gesto de llave/tornillo |
| 🖐️ 5 dedos desplegados | Abrir menú principal | Mostrar todos los controles |
| 👍 Pulgar arriba | Cambiar modo visual | Toggle entre modos |
| 🤙 Teléfono (pulgar+meñique) | Cambiar color | Ciclar por paleta de colores |

#### Tareas

- [ ] Extracción de los 21 landmarks de MediaPipe por mano
- [ ] Cálculo de ángulos y distancias entre landmarks
- [ ] Clasificador de gestos estáticos (postura de la mano)
- [ ] Reconocimiento de gestos dinámicos (trayectoria de movimiento)
- [ ] Sistema de estados para evitar activaciones accidentales (cooldown)
- [ ] Modo debug: visualizar nombre del gesto detectado en pantalla
- [ ] Calibración de sensibilidad por usuario

#### Entregable
> Sistema capaz de detectar los 9 gestos con precisión >85% en condiciones normales de iluminación.

---

### ✅ Fase 5 — Integración Gestos + Modelo 3D

**Objetivo:** Conectar los gestos detectados con las transformaciones del modelo en tiempo real.

**Duración estimada:** 2 semanas

#### Tareas

- [ ] Mapear rotación de mano → rotación del modelo (cuaterniones)
- [ ] Mapear distancia entre manos → factor de escala (zoom)
- [ ] Suavizado de movimiento (interpolación / filtro de Kalman) para evitar temblor
- [ ] Umbrales de activación para evitar micro-movimientos accidentales
- [ ] Sistema de modos: detectar cuándo se cambia de gesto sin conflictos
- [ ] Rotación libre en los 3 ejes (X, Y, Z) de forma intuitiva
- [ ] Reset de transformaciones con gesto específico

#### Algoritmo de suavizado

```python
# Filtro exponencial simple para suavizar posición de la mano
alpha = 0.3  # factor de suavizado (0=sin respuesta, 1=sin suavizado)
smooth_pos = alpha * raw_pos + (1 - alpha) * prev_pos
```

#### Entregable
> Manipulación fluida del modelo 3D con las manos: rotar, hacer zoom y mover sin latencia perceptible.

---

### ✅ Fase 6 — Selector de Archivos por Gestos

**Objetivo:** Abrir modelos 3D desde el sistema de archivos usando únicamente gestos.

**Duración estimada:** 1–2 semanas

#### Tareas

- [ ] Panel flotante de explorador de archivos renderizado en OpenGL
- [ ] Cursor gestual controlado por dedo índice
- [ ] Navegación por carpetas con gestos de selección
- [ ] Filtro visual de archivos soportados (mostrar solo 3D)
- [ ] Preview de nombre/ícono del archivo al apuntar
- [ ] Confirmación de apertura con gesto "OK"
- [ ] Historial de archivos recientes (últimos 5 modelos)
- [ ] Fallback: detección de archivos arrastrados a la ventana (drag & drop del OS)

#### Entregable
> El usuario puede navegar carpetas y abrir un modelo 3D sin tocar mouse ni teclado.

---

### ✅ Fase 7 — Controles Avanzados del Modelo

**Objetivo:** Funcionalidades adicionales de manipulación y visualización.

**Duración estimada:** 2 semanas

#### Tareas

- [ ] **Cambio de color:** paleta de 8 colores accesible por gesto
- [ ] **Cambio de modo:** ciclar entre SOLID / WIREFRAME / POINTS
- [ ] **Ajuste de iluminación:** cambiar posición de la fuente de luz con gesto
- [ ] **Secciones:** cortar el modelo con un plano virtual (opcional avanzado)
- [ ] **Información del modelo:** mostrar stats (vértices, triángulos, tamaño)
- [ ] **Multi-modelo:** cargar más de un modelo simultáneamente
- [ ] **Exportar vista:** captura de pantalla del modelo con un gesto

#### Entregable
> Suite completa de controles del modelo accesibles por gestos, con feedback visual de cada acción.

---

### ✅ Fase 8 — Pulido y UX Gestual

**Objetivo:** Hacer la experiencia cómoda, intuitiva y robusta.

**Duración estimada:** 2–3 semanas

#### Tareas

- [ ] Menú de ayuda contextual (mostrar gestos disponibles con íconos)
- [ ] Feedback visual cuando se detecta un gesto (highlight, animación)
- [ ] Feedback de audio (sonido sutil al confirmar acción) — opcional
- [ ] Reducción de fatiga: auto-pausa si no hay movimiento por N segundos
- [ ] Adaptación a diferentes condiciones de iluminación (normalización de imagen)
- [ ] Soporte para cámaras de profundidad (Intel RealSense, Kinect) — opcional
- [ ] Configuración guardable por usuario (sensibilidad, colores, modos)
- [ ] Modo presentación: fondo negro, sin UI debug

#### Entregable
> Aplicación usable por alguien que nunca la ha visto antes, con guía visual integrada.

---

## 📦 Dependencias Completas

```txt
# requirements.txt

# Visión por computadora y detección de manos
opencv-python>=4.8.0
mediapipe>=0.10.0

# Renderizado 3D
PyOpenGL>=3.1.7
PyOpenGL_accelerate>=3.1.7
glfw>=2.6.0

# Carga de modelos 3D (soporte universal)
open3d>=0.18.0
trimesh>=4.0.0
pyassimp>=5.3.0

# Matemáticas y procesamiento
numpy>=1.24.0
scipy>=1.11.0        # filtros de suavizado

# Utilidades
Pillow>=10.0.0       # manejo de imágenes/texturas
PyYAML>=6.0          # configuración de usuario
```

---

## 🗓️ Cronograma Sugerido

```
Semana 1-2   │ Fase 1 — Infraestructura base
Semana 3-4   │ Fase 2 — Carga de modelos + Fase 3 (inicio renderizado)
Semana 5-6   │ Fase 3 — Renderizado avanzado
Semana 7-8   │ Fase 4 — Diccionario de gestos
Semana 9-10  │ Fase 5 — Integración gestos + 3D
Semana 11    │ Fase 6 — Selector de archivos
Semana 12-13 │ Fase 7 — Controles avanzados
Semana 14-16 │ Fase 8 — Pulido y UX
```

---

## 🚀 MVP (Producto Mínimo Viable)

El MVP se considera alcanzado al completar las **Fases 1–5**, con:

- Carga de modelos `.obj` y `.glb`
- Rotación y zoom con gestos
- Modo sólido y wireframe
- Sin selector de archivos gestual (ruta por argumento de consola)

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Falsos positivos en gestos | Alto | Cooldown entre acciones + umbral de confianza |
| Latencia alta en detección | Alto | Procesar en thread separado, reducir resolución de cámara |
| Fatiga del usuario | Medio | Gestos cortos, auto-pausa, soporte teclado como fallback |
| Formatos 3D no compatibles | Bajo | Pipeline multicapa (Open3D → Trimesh → Assimp) |
| Iluminación variable | Medio | Normalización de histograma en pre-procesado |

---

*Documento generado para planificación del proyecto. Versión 1.0*
