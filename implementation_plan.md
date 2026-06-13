# Fase 7 — Controles Avanzados del Modelo

## Contexto

Tras un análisis exhaustivo del código, el proyecto tiene **8 archivos Python**, un modelo de IA (hand_landmarker.task), y un pipeline de renderizado con OpenGL de función fija. La arquitectura es modular: `config.py` como bus de estado global, `gesture_controller.py` para gestos, `opengl_renderer.py` para renderizado, `ui_overlay.py` para interfaz, `input_handlers.py` para entradas, `camera_tracker.py` para seguimiento de manos, `model_loader.py` para carga de modelos, y `main.py` como orquestador.

### Bugs Encontrados (Se corregirán antes de implementar)
- `was_pinch` declarado en `global` (línea 105) pero **nunca definido** a nivel de módulo → Crash latente
- `smooth_fist_pos` nunca inicializado a nivel de módulo (sólo funciona por casualidad)
- `config.py` tiene variables muertas de la Fase 6: `is_explorer_open`, `current_path`, `recent_files`, `cursor_x`, `cursor_y`, `explorer_scroll_y`, `hovered_item`, `window_width`, `window_height`
- `input_handlers.py` tiene función `handle_gesture_click()` muerta (nunca llamada)
- `ui_overlay.py` tiene función `get_explorer_texture()` muerta

---

## User Review Required

> [!IMPORTANT]
> **Cambio de modo ya implementado.** El gesto ☝️☝️ (2 índices) ya cicla entre SOLID/WIREFRAME/SOLID+WIRE/POINTS. Esta tarea de la Fase 7 ya está completada.

> [!IMPORTANT]
> **Secciones (Clip Planes):** Usaré `glClipPlane` del pipeline de función fija de OpenGL, lo cual permite cortar el modelo con un plano sin necesidad de shaders. El plano se controlará con teclado (tecla `S` para activar/desactivar, scroll para mover el plano).

> [!WARNING]
> **Multi-modelo:** Cambiaré `config.loaded_model` de un solo modelo a una lista de modelos. Cada modelo nuevo se añadirá a la lista (máximo 5). Se podrá navegar entre ellos con las teclas `←` y `→`, o eliminar el actual con `Delete`. Todos se renderizarán simultáneamente, pero solo el "activo" será el que se manipule.

> [!IMPORTANT]
> **Gestos nuevos vs Teclado:** Para evitar saturar el espacio de gestos de una sola mano (ya tenemos 5 gestos asignados), los controles avanzados usarán **atajos de teclado** con feedback visual en pantalla. Solo la **captura de pantalla** usará un gesto nuevo (✊✊ Doble Puño = Captura).

---

## Open Questions

> [!IMPORTANT]
> **Paleta de colores:** Los 8 colores propuestos son: Gris (default), Rojo, Verde, Azul, Amarillo, Cian, Magenta, Naranja. ¿Quieres otros colores o estos te parecen bien?

> [!IMPORTANT]
> **Gesto de captura:** Propongo usar ✊✊ (ambos puños cerrados) para tomar una captura de pantalla. ¿Te parece bien o prefieres otro gesto?

---

## Proposed Changes

### Componente 0: Limpieza de Bugs y Código Muerto

#### [MODIFY] [config.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/config.py)
- Eliminar variables muertas de Fase 6: `is_explorer_open`, `current_path`, `recent_files`, `cursor_x`, `cursor_y`, `explorer_scroll_y`, `hovered_item`, `window_width`, `window_height`
- Añadir nuevas variables para Fase 7 (ver componentes abajo)

#### [MODIFY] [gesture_controller.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/gesture_controller.py)
- Corregir `was_pinch` → eliminarlo de la declaración global (ya no existe)
- Inicializar `smooth_fist_pos = None` a nivel de módulo
- Eliminar `import os` si existe

#### [MODIFY] [input_handlers.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/input_handlers.py)
- Eliminar función muerta `handle_gesture_click()`
- Eliminar `import os` residual

#### [MODIFY] [ui_overlay.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/ui_overlay.py)
- Eliminar función muerta `get_explorer_texture()`
- Eliminar `import os` residual

---

### Componente 1: Cambio de Color (Tecla `C`)

#### [MODIFY] [config.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/config.py)
- Añadir `color_palette`: lista de 8 tuplas RGB
- Añadir `current_color_idx`: índice actual (0 = gris default)
- Añadir `show_color_feedback`: bool y `color_feedback_time`: float para animación temporal

#### [MODIFY] [input_handlers.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/input_handlers.py)
- Añadir tecla `C` en `key_callback` → cicla `current_color_idx`
- Activar `show_color_feedback` con timestamp para mostrar el color brevemente

#### [MODIFY] [opengl_renderer.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/opengl_renderer.py)
- En `render_model_geometry()`: si el modelo NO tiene colores por vértice, aplicar `glColor3f` con el color seleccionado de la paleta antes de dibujar
- Si el modelo SÍ tiene colores, multiplicar/mezclar con el color de la paleta como tinte

#### [MODIFY] [ui_overlay.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/ui_overlay.py)
- Dibujar feedback visual temporal: un cuadrado del color seleccionado con el nombre del color durante 2 segundos tras presionar `C`

---

### Componente 2: Ajuste de Iluminación (Tecla `L` + Ratón/Fist)

#### [MODIFY] [config.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/config.py)
- Añadir `light_mode`: bool (False por defecto). Cuando está activo, el Fist mueve la luz en vez del modelo
- Añadir `light_yaw`, `light_pitch`: floats (posición de la luz en coordenadas esféricas)

#### [MODIFY] [input_handlers.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/input_handlers.py)
- Tecla `L` → toggle `light_mode`. Cuando está activo, el arrastre del ratón mueve la luz en vez de rotar el modelo

#### [MODIFY] [gesture_controller.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/gesture_controller.py)
- Cuando `config.light_mode == True` y gesto es FIST: modificar `config.light_yaw/pitch` en vez de `config.camera_yaw/pitch`

#### [MODIFY] [opengl_renderer.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/opengl_renderer.py)
- En `set_lighting()`: calcular posición de luz desde `light_yaw` y `light_pitch` usando coordenadas esféricas: `x = cos(pitch)*sin(yaw)`, `y = sin(pitch)`, `z = cos(pitch)*cos(yaw)`

#### [MODIFY] [ui_overlay.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/ui_overlay.py)
- Cuando `light_mode` activo: mostrar indicador "☀️ LUZ" en amarillo en la UI

---

### Componente 3: Secciones / Clip Plane (Tecla `S`)

#### [MODIFY] [config.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/config.py)
- Añadir `clip_plane_enabled`: bool (False)
- Añadir `clip_plane_position`: float (0.0, rango -2.0 a 2.0)
- Añadir `clip_plane_axis`: int (0=X, 1=Y, 2=Z)

#### [MODIFY] [input_handlers.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/input_handlers.py)
- Tecla `S` → toggle `clip_plane_enabled`
- Tecla `X` (cuando clip activo) → ciclar eje del plano (X→Y→Z→X)
- Cuando clip activo: scroll del ratón mueve `clip_plane_position` en vez de zoom

#### [MODIFY] [opengl_renderer.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/opengl_renderer.py)
- En `draw_model()` y `draw_cube()`: si `clip_plane_enabled`, activar `GL_CLIP_PLANE0` con la ecuación del plano según el eje seleccionado
- Dibujar un quad semitransparente rojo en la posición del corte para visualizar el plano

---

### Componente 4: Información del Modelo (Tecla `I`)

#### [MODIFY] [config.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/config.py)
- Añadir `show_model_info`: bool (False)

#### [MODIFY] [model_loader.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/model_loader.py)
- Añadir a `ModelData`: atributos `vertex_count`, `face_count`, `file_name`, `file_size_mb`
- Poblar estos datos durante la carga

#### [MODIFY] [ui_overlay.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/ui_overlay.py)
- Cuando `show_model_info == True`: dibujar panel con stats del modelo (vértices, triángulos, nombre, tamaño) en la esquina inferior derecha

#### [MODIFY] [input_handlers.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/input_handlers.py)
- Tecla `I` → toggle `show_model_info`

---

### Componente 5: Multi-Modelo (Teclas `←` `→` `Delete`)

#### [MODIFY] [config.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/config.py)
- Cambiar `loaded_model` → `loaded_models`: lista de hasta 5 ModelData
- Añadir `active_model_idx`: int (índice del modelo activo)

#### [MODIFY] [input_handlers.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/input_handlers.py)
- Al cargar un modelo: añadir a la lista en vez de reemplazar (máx 5, si hay 5 reemplaza el activo)
- Tecla `←` → modelo anterior
- Tecla `→` → modelo siguiente
- Tecla `Delete` → eliminar modelo activo de la lista

#### [MODIFY] [opengl_renderer.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/opengl_renderer.py)
- Refactorizar `draw_model()` para renderizar todos los modelos de la lista
- El modelo activo se renderiza con colores normales; los inactivos con transparencia reducida (alpha 0.3)
- Invalidar display list cuando se elimina un modelo

#### [MODIFY] [main.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/main.py)
- Actualizar todas las referencias a `config.loaded_model` → usar `config.loaded_models` y `config.active_model_idx`

#### [MODIFY] [ui_overlay.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/ui_overlay.py)
- Mostrar indicador "Modelo 2/3" cuando hay múltiples modelos cargados

---

### Componente 6: Exportar Vista / Captura de Pantalla (Tecla `P` + Gesto ✊✊)

#### [MODIFY] [config.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/config.py)
- Añadir `take_screenshot`: bool (False) — flag de un solo frame
- Añadir `screenshot_feedback_time`: float (0.0) — para animación de flash

#### [MODIFY] [gesture_controller.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/gesture_controller.py)
- Añadir `GESTURE_TWO_FISTS` = "TWO_FISTS"
- En `process_gestures()`: si 2 manos detectadas y ambas son FIST → activar `config.take_screenshot`
- Lógica de one-shot (como `was_ok`)

#### [MODIFY] [input_handlers.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/input_handlers.py)
- Tecla `P` → activar `config.take_screenshot`

#### [MODIFY] [main.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/main.py)
- Después de `swap_buffers`: si `config.take_screenshot == True`:
  1. `glReadPixels` para capturar el framebuffer completo
  2. Convertir a imagen OpenCV (BGR, flip vertical)
  3. Guardar en `capturas/captura_YYYYMMDD_HHMMSS.png`
  4. Resetear flag
  5. Activar `screenshot_feedback_time` para flash visual

#### [MODIFY] [ui_overlay.py](file:///c:/Users/chimi/Documents/GitHub/Visor3D/ui_overlay.py)
- Flash blanco temporal (200ms) cuando se toma una captura, con texto "📸 Captura guardada"

---

## Resumen de Atajos de Teclado (Tras Fase 7)

| Tecla | Acción |
|---|---|
| `O` | Abrir modelo |
| `V` | Ciclar vista (Split/HUD/AR) |
| `M` | Ciclar modo render |
| `G` | Toggle grid |
| `C` | Ciclar color del modelo |
| `L` | Toggle modo iluminación |
| `S` | Toggle sección/clip plane |
| `X` | Ciclar eje del clip (cuando S activo) |
| `I` | Toggle info del modelo |
| `←` `→` | Navegar entre modelos |
| `Delete` | Eliminar modelo activo |
| `P` | Captura de pantalla |

## Resumen de Gestos (Tras Fase 7)

| Gesto | Acción |
|---|---|
| ✋ Palma Abierta | Mover/Rotar modelo |
| ✊ Puño Cerrado | Rotar X/Y (o mover luz si modo luz activo) |
| ✌️ Dos Dedos (V) | Rotar Z |
| 🤏 Pulgar+Índice | Zoom |
| ☝️☝️ 2 Índices | Cambiar modo render |
| ✋✋ 2 Palmas | Reset cámara |
| ✊✊ 2 Puños | Captura de pantalla |

---

## Verification Plan

### Automated Tests
- `python -c "import config; import gesture_controller; import opengl_renderer; import model_loader; import ui_overlay; import input_handlers; print('All imports OK')"` — verificar que no hay errores de importación
- `python main.py` — verificar que la aplicación inicia sin crashes

### Manual Verification
1. Presionar cada tecla nueva (C, L, S, X, I, P, ←, →, Delete) y verificar feedback visual
2. Cargar 3 modelos y navegar entre ellos con flechas
3. Activar sección y mover el plano con scroll
4. Cambiar color y verificar que el modelo cambia
5. Presionar L y arrastrar con ratón para mover la luz
6. Hacer gesto ✊✊ y verificar que se guarda la captura
7. Verificar que los gestos existentes siguen funcionando correctamente
