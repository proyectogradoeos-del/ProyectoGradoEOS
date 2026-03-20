# Documentación del Módulo To-Do EOS

## Funcionalidades Implementadas

### 1. Modelo de Datos (`eos_todo.py`)
- **Campos principales**:
  - `name`: Título de la tarea (requerido)
  - `description`: Descripción detallada
  - `owner_id`: Usuario asignado (por defecto el usuario actual)
  - `due_date`: Fecha de vencimiento
  - `status`: Estado de la tarea (Por Hacer, En Curso, En Revisión, Finalizado, Cancelado)
  - `progress`: Progreso calculado automáticamente basado en el estado
  - `rock_id`: Relación con Rocks (opcional)

- **Métodos disponibles**:
  - `action_start_progress()`: Marcar como "En Curso"
  - `action_mark_for_review()`: Marcar para "En Revisión"
  - `action_mark_done()`: Marcar como "Finalizado"
  - `action_reset_to_todo()`: Volver a "Por Hacer"

### 2. Vistas Implementadas

#### Vista de Lista (`view_eos_todo_tree`)
- Muestra todas las tareas en formato tabla
- Colores diferentes según el estado
- Barra de progreso visual
- Campos: Nombre, Asignado, Fecha vencimiento, Estado, Progreso, Fecha creación

#### Vista de Formulario (`view_eos_todo_form`)
- Formulario completo para editar tareas
- Botones de estado en el header
- StatusBar para visualizar el flujo de trabajo
- Notebook con descripción detallada

#### Vista de Búsqueda (`view_eos_todo_search`)
- Filtros predefinidos:
  - "Mis Tareas": Solo tareas asignadas al usuario actual
  - "Pendientes": Tareas no completadas
  - "Completadas": Tareas finalizadas
  - "Vencidas": Tareas con fecha pasada no completadas
- Agrupación por: Estado, Asignado, Fecha de vencimiento

### 3. Tablero Kanban (`todo_board.js`)

#### Funcionalidades del Tablero:
- **Vista de columnas**: 4 columnas (Por Hacer, En Curso, En Revisión, Finalizado)
- **Contadores**: Número de tareas en cada estado
- **Agregar tarea**: Input directo en el tablero
- **Editar tarea**: Click en cualquier tarjeta abre el formulario
- **Eliminar tarea**: Botón de eliminar con confirmación
- **Progreso visual**: Barra de progreso en cada tarjeta
- **Información completa**: Nombre, asignado, fecha vencimiento

#### Interacciones:
- **Crear**: Escribir en el input y presionar Enter o click en "Agregar"
- **Editar**: Click en cualquier parte de la tarjeta o botón "Editar"
- **Eliminar**: Botón rojo con icono de basura + confirmación
- **Navegación**: Carga automática y actualización en tiempo real

### 4. Estilos y UI (`dashboard.css`)
- Diseño responsive para móviles y tablets
- Colores temáticos por estado
- Animaciones y transiciones suaves
- Efectos hover en tarjetas y botones
- Tipografía moderna (Inter font)

## Cómo Usar

### Acceso al Módulo
1. Instalar el módulo `mi90_eos`
2. Ir al menú "EOS DATA" > "To-Do"
3. Se abre automáticamente el tablero Kanban

### Crear Nueva Tarea
1. En el tablero: escribir en el campo "Agregar nueva tarea..." y presionar Enter
2. En vista lista: botón "Crear" para formulario completo

### Gestionar Tareas
1. **Cambiar estado**: Click en tarjeta → formulario → botones de estado
2. **Asignar usuario**: Campo "Owner" en formulario
3. **Establecer fecha**: Campo "Due Date" en formulario
4. **Relacionar con Rock**: Campo "Related Rock" en formulario

### Filtros y Búsquedas
- Usar la vista de lista para filtros avanzados
- Filtro "Mis Tareas" para ver solo asignaciones propias
- Agrupar por estado para organizar mejor

## Estructura de Archivos

```
models/
  eos_todo.py                 # Modelo de datos

views/
  eos_todo_views.xml         # Definiciones de vistas

static/src/
  js/todo_board.js           # Lógica del tablero Kanban
  css/dashboard.css          # Estilos visuales
  xml/todos.xml              # Templates de frontend

security/
  ir.model.access.csv        # Permisos de acceso
```

## Validaciones y Reglas de Negocio

1. **Nombre requerido**: No se puede crear tarea sin nombre
2. **Progreso automático**: Se calcula según el estado:
   - Por Hacer: 0%
   - En Curso: 40%
   - En Revisión: 75%
   - Finalizado: 100%
   - Cancelado: 0%

3. **Usuario por defecto**: Se asigna automáticamente al usuario actual
4. **Fechas de actualización**: Se actualizan automáticamente

## Próximas Mejoras Sugeridas

1. **Drag & Drop**: Arrastrar tarjetas entre columnas
2. **Notificaciones**: Alertas por tareas vencidas
3. **Comentarios**: Sistema de comentarios en tareas
4. **Archivos adjuntos**: Subir documentos a las tareas
5. **Dashboard analytics**: Gráficos de productividad
6. **Plantillas**: Tareas predefinidas frecuentes