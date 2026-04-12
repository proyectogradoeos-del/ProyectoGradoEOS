# EOS Center Data — Manual Técnico Completo
### Ficha Metodológica para Desarrolladores — Versión 100%
**Proyecto:** EOS Center Data — TLP Holding (Technology Latam Partners Colombia S.A.S.)
**Universidad:** Universidad El Bosque — Ingeniería de Sistemas
**Versión del módulo:** 17.0.4.0.0
**Autores:** Carlos Alfredo Gómez Vega · Juan Pablo Carreño Moreno · Kevin Santiago García Pérez
**Director:** Carlos Ignácio Delgado Román

---

## Tabla de Contenido

1. [Introducción y Contexto del Proyecto](#1-introducción-y-contexto-del-proyecto)
2. [Requisitos del Entorno](#2-requisitos-del-entorno)
3. [Estructura Completa del Módulo](#3-estructura-completa-del-módulo)
4. [Guía de Instalación Paso a Paso](#4-guía-de-instalación-paso-a-paso)
5. [Sistema de Seguridad y Roles](#5-sistema-de-seguridad-y-roles)
6. [Componente 1 — VISIÓN](#6-componente-1--visión)
7. [Componente 2 — PERSONAS](#7-componente-2--personas)
8. [Componente 3 — DATOS](#8-componente-3--datos)
9. [Componente 4 — PROBLEMAS](#9-componente-4--problemas)
10. [Componente 5 — PROCESOS](#10-componente-5--procesos)
11. [Componente 6 — TRACCIÓN](#11-componente-6--tracción)
12. [Patrones Técnicos de Odoo 17 Usados en el Módulo](#12-patrones-técnicos-de-odoo-17-usados-en-el-módulo)
13. [Guía de Uso Operativo para TLP Holding](#13-guía-de-uso-operativo-para-tlp-holding)
14. [Solución de Problemas Comunes](#14-solución-de-problemas-comunes)
15. [Glosario EOS y Técnico](#15-glosario-eos-y-técnico)

---

## 1. Introducción y Contexto del Proyecto

### ¿Qué es EOS Center Data?

**EOS Center Data** es un módulo personalizado desarrollado sobre **Odoo 17** que digitaliza e integra los seis componentes de la metodología **EOS® (Entrepreneurial Operating System)** en un único entorno centralizado para TLP Holding.

El problema que resuelve: TLP Holding gestionaba EOS mediante hojas de cálculo, correos y documentos dispersos, lo que generaba pérdida de trazabilidad, datos desactualizados y desalineación entre equipos.

### Los 6 Componentes EOS implementados

| # | Componente | Herramienta Principal | Modelos Python |
|---|---|---|---|
| 1 | **Visión** | V/TO (Vision/Traction Organizer) | `eos.vision`, `eos.vision.rock`, `eos.vision.score` |
| 2 | **Personas** | Accountability Chart + Evaluación GWC | `eos.seat`, `eos.people.evaluation` |
| 3 | **Datos** | Scorecard Semanal + OKRs | `eos.scorecard`, `eos.kpi`, `eos.kpi.record`, `eos.okr`, `eos.okr.key.result` |
| 4 | **Problemas** | Issues List + Proceso IDS | `eos.issue` |
| 5 | **Procesos** | Documentador de Procesos | `eos.process`, `eos.process.step` |
| 6 | **Tracción** | L10 Meeting + To-Dos | `eos.meeting`, `eos.meeting.attendee`, `eos.todo` |

**Total: 14 modelos · ~2.400 líneas de Python · ~1.800 líneas de XML**

---

## 2. Requisitos del Entorno

### Software requerido

| Componente | Versión | Notas |
|---|---|---|
| **Odoo** | 17.0 | Community o Enterprise. Ambas son compatibles. |
| **Python** | 3.10 o 3.11 | Incluido con Odoo 17. No instalar aparte. |
| **PostgreSQL** | 14, 15 o 16 | Motor de base de datos. Se recomienda v15. |
| **Sistema Operativo** | Ubuntu 22.04 LTS | También funciona en Debian 11, Ubuntu 24 o WSL2. |
| **Git** | Cualquier versión reciente | Para clonar el repositorio del módulo. |

### Módulos Odoo requeridos (dependencias)

```python
'depends': ['base', 'mail', 'hr']
```

| Módulo | ¿Qué aporta al proyecto? |
|---|---|
| `base` | Modelos base: `res.company`, `res.users`, `res.currency` |
| `mail` | Chatter (historial de cambios, mensajes internos, actividades) |
| `hr` | `hr.employee` y `hr.department` para el módulo de Personas |

Estos módulos están incluidos en Odoo 17 por defecto. **No requieren instalación adicional.**

---

## 3. Estructura Completa del Módulo

```
eos_center_data/
│
├── __init__.py                        ← Punto de entrada Python
├── __manifest__.py                    ← Metadatos del módulo (nombre, versión, dependencias)
│
├── models/                            ← Lógica de negocio (Python)
│   ├── __init__.py                    ← Importa todos los modelos en orden correcto
│   ├── eos_vision.py                  ← Componente 1: EosVision + EosVisionRock
│   ├── eos_vision_score.py            ← Componente 1: EosVisionScore
│   ├── eos_people.py                  ← Componente 2: EosSeat + EosPeopleEvaluation
│   ├── eos_data.py                    ← Componente 3: EosScorecard + EosKpi + EosOkr...
│   ├── eos_issues.py                  ← Componente 4: EosIssue
│   ├── eos_processes.py               ← Componente 5: EosProcess + EosProcessStep
│   └── eos_traction.py                ← Componente 6: EosMeeting + EosTodo...
│
├── views/                             ← Interfaz de usuario (XML)
│   ├── eos_vision_views.xml           ← Vistas: V/TO y Rocas
│   ├── eos_vision_score_views.xml     ← Vistas: Puntuación de Visión
│   ├── eos_people_views.xml           ← Vistas: Accountability Chart y GWC
│   ├── eos_data_views.xml             ← Vistas: Scorecard y OKRs
│   ├── eos_issues_views.xml           ← Vistas: Issues (Kanban, Lista, Formulario)
│   ├── eos_processes_views.xml        ← Vistas: Procesos Críticos
│   ├── eos_traction_views.xml         ← Vistas: L10 Meeting y To-Dos
│   └── eos_menu_views.xml             ← Estructura de menús de navegación
│
├── security/
│   ├── eos_security.xml               ← Grupos de usuarios y categoría de la app
│   └── ir.model.access.csv           ← Permisos CRUD por modelo y grupo
│
├── data/
│   └── eos_vision_data.xml            ← Parámetros de configuración iniciales
│
└── static/
    ├── description/
    │   └── icon.png                   ← Ícono del módulo (64x64 px, PNG)
    └── src/css/
        └── eos_styles.css             ← Estilos visuales personalizados
```

### Orden de carga en `__manifest__.py`

> **⚠️ CRÍTICO:** El orden de archivos en la lista `data` del manifest NO es arbitrario. Odoo los carga en secuencia y los archivos posteriores pueden referenciar IDs definidos en archivos anteriores. Si el orden es incorrecto, la instalación falla.

**Orden correcto obligatorio:**
1. `security/eos_security.xml` — define los grupos de usuarios
2. `security/ir.model.access.csv` — define permisos (referencia grupos del paso 1)
3. `data/*.xml` — datos de configuración
4. `views/*.xml` — vistas (referencian grupos del paso 1)
5. `views/eos_menu_views.xml` — menús (deben ir al FINAL, referencian acciones de los pasos anteriores)

---

## 4. Guía de Instalación Paso a Paso

### Paso 1: Copiar el módulo al servidor

```bash
# Navegar a la carpeta de addons personalizados de Odoo
cd /opt/odoo/custom_addons/

# Opción A: Copiar desde un directorio local
cp -r /ruta/a/eos_center_data .

# Opción B: Clonar desde repositorio Git
git clone https://github.com/tu_org/eos_center_data.git
```

### Paso 2: Verificar el archivo de configuración de Odoo

Abrir `/etc/odoo/odoo.conf` y asegurarse de que la ruta `custom_addons` esté incluida:

```ini
[options]
addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom_addons
db_host = localhost
db_port = 5432
db_user = odoo
db_password = tu_password
```

### Paso 3: Actualizar la lista de módulos disponibles

```bash
# Reiniciar el servicio de Odoo (recarga los addons disponibles)
sudo systemctl restart odoo17

# Verificar que el servicio arrancó sin errores
sudo journalctl -u odoo17 -n 50
```

### Paso 4: Instalar desde la interfaz web

1. Ingresar a Odoo como **Administrador**
2. Ir al menú principal → **Aplicaciones**
3. En la barra de búsqueda, desactivar el filtro **"Aplicaciones"** (para ver también módulos)
4. Buscar: `EOS Center Data`
5. Hacer clic en **Instalar**
6. Esperar a que finalice (puede tardar 30-60 segundos)

### Paso 5: Verificar la instalación

Después de la instalación:
- El ícono **"EOS Center Data"** debe aparecer en el menú principal de Odoo
- Ir a **Ajustes → Usuarios → Seleccionar usuario de prueba → Sección "EOS Center Data"**
- Asignar el rol **"Directivo / Leadership Team"** para acceso completo
- Navegar a **EOS Center Data → 1. Visión → V/TO** y crear el primer registro

### Paso 6: Agregar el ícono del módulo

Crear o copiar una imagen PNG de exactamente **64×64 píxeles** en:
```
eos_center_data/static/description/icon.png
```

Si no se agrega, Odoo mostrará un ícono genérico. No afecta la funcionalidad.

---

## 5. Sistema de Seguridad y Roles

### Jerarquía de grupos (de menor a mayor acceso)

```
Administrador EOS (acceso total + configuración)
    └── Directivo / Leadership Team (gestión estratégica completa)
            └── Líder de Área (gestión operativa y de equipo)
                    └── Colaborador (solo lectura — ver visión y compromisos)
```

Los grupos en Odoo son **acumulativos**: cada nivel hereda todos los permisos del nivel inferior (campo `implied_ids` en el XML de seguridad).

### Tabla resumen de permisos por componente

| Componente / Modelo | Colaborador | Líder de Área | Directivo | Admin |
|---|:---:|:---:|:---:|:---:|
| V/TO (`eos.vision`) | 👁 | R+W | R+W+C | Todo |
| Rocas (`eos.vision.rock`) | 👁 | R+W+C | R+W+C | Todo |
| Puntuación Visión | 👁 | 👁 | R+W+C | Todo |
| Asientos AC (`eos.seat`) | 👁 | R+W | R+W+C | Todo |
| Evaluación GWC | — | — | R+W+C | Todo |
| Scorecard (`eos.scorecard`) | 👁 | R+W | R+W+C | Todo |
| KPI (`eos.kpi`) | 👁 | R+W+C | R+W+C | Todo |
| OKR (`eos.okr`) | 👁 | R+W | R+W+C | Todo |
| Issues (`eos.issue`) | 👁 | R+W+C | R+W+C | Todo |
| Procesos (`eos.process`) | 👁 | R+W | R+W+C | Todo |
| L10 Meeting (`eos.meeting`) | — | R+W+C | R+W+C | Todo |
| To-Dos (`eos.todo`) | 👁 | R+W+C | R+W+C | Todo |

> **Convención:** 👁 = solo lectura · R = leer · W = escribir · C = crear · Todo = incluye eliminar

### Cómo asignar roles a usuarios

1. Ir a **Ajustes → Usuarios y Empresas → Usuarios**
2. Seleccionar el usuario
3. En la sección **"EOS Center Data"** del formulario del usuario, elegir el rol
4. Guardar. El cambio aplica inmediatamente.

---

## 6. Componente 1 — VISIÓN

### Propósito en EOS

El componente Visión centraliza el **V/TO (Vision/Traction Organizer)**, que es el documento estratégico maestro de EOS. Responde a dos preguntas fundamentales: *¿A dónde vamos?* y *¿Cómo llegamos allá?*

### Modelos Python

#### `EosVision` — El V/TO
**Archivo:** `models/eos_vision.py`
**Tabla en BD:** `eos_vision`

```python
class EosVision(models.Model):
    _name = 'eos.vision'
    _inherit = ['mail.thread', 'mail.activity.mixin']
```

**Herencia `mail.thread`:** agrega el Chatter al formulario. Cada campo con `tracking=True` registra automáticamente quién cambió qué y cuándo.

**Campos clave:**

| Campo | Tipo | Propósito |
|---|---|---|
| `name` | `Char` | Nombre del V/TO. Ej: "V/TO 2025 - TLP Holding" |
| `state` | `Selection` | Ciclo de vida: Borrador → Revisión → Aprobado → Archivado |
| `core_values` | `Text` | Los 3-7 valores fundamentales de la empresa |
| `core_focus_purpose` | `Text` | El propósito profundo (el "por qué") |
| `goal_10_years` | `Text` | BHAG: objetivo grande y audaz a 10 años |
| `goal_3_years_revenue` | `Monetary` | Meta de ingresos a 3 años |
| `annual_rocks_ids` | `One2many` | Rocas (prioridades anuales) del V/TO |
| `vision_score_avg` | `Float` (compute) | Promedio de puntuaciones de visión del equipo |

**Flujo de estados:**
```
draft → review → approved → archived
  ↑_________|   (puede volver a draft si es rechazado)
```

**Métodos de acción (botones de estado):**
```python
def action_set_review(self):   # Envía a revisión
def action_approve(self):      # Aprueba y guarda fecha de revisión
def action_set_draft(self):    # Regresa a borrador
def action_archive_vto(self):  # Archiva (inactiva) el V/TO
```

#### `EosVisionRock` — Rocas
**Tabla en BD:** `eos_vision_rock`

Una Roca es una prioridad estratégica de 90 días. Cada Roca tiene un único dueño (`owner_id`) y un estado de seguimiento:

```python
state = fields.Selection([
    ('on_track', 'En Camino ✅'),
    ('off_track', 'Fuera de Camino ⚠️'),
    ('done', 'Completada ✔'),
    ('not_started', 'No Iniciada'),
    ('cancelled', 'Cancelada'),
])
```

El campo `sequence` con `widget="handle"` en la vista permite arrastrar y reordenar las Rocas visualmente.

**`@api.onchange('date_deadline')`** — Infiere automáticamente el trimestre (Q1-Q4) cuando el usuario selecciona la fecha límite.

#### `EosVisionScore` — Puntuación de Visión
**Archivo:** `models/eos_vision_score.py`
**Tabla en BD:** `eos_vision_score`

Encuesta de 8 preguntas (escala 1-10) que mide la alineación del equipo con la visión.

**Fórmula de cálculo:**
```python
score_total = sum(8 preguntas)          # Máximo: 80 puntos
score_percentage = (total / 80) * 100   # Porcentaje

# Nivel de alineación:
if percentage >= 80: alignment_level = 'high'     # Alineado ✅
elif percentage >= 60: alignment_level = 'medium'  # En proceso ⚠️
else: alignment_level = 'low'                      # Desalineado 🔴
```

---

## 7. Componente 2 — PERSONAS

### Propósito en EOS

El componente Personas responde: *¿Tenemos las personas correctas en los puestos correctos?*

Herramienta central: **Accountability Chart (AC)** — un mapa de responsabilidades (no un organigrama tradicional). Cada "Asiento" tiene funciones específicas y UN titular responsable.

### Modelos Python

#### `EosSeat` — Asiento del Accountability Chart
**Archivo:** `models/eos_people.py`
**Tabla en BD:** `eos_seat`

Permite construir el AC de forma jerárquica mediante el campo:
```python
parent_seat_id = fields.Many2one('eos.seat', ...)   # Relación padre-hijo
child_seat_ids = fields.One2many('eos.seat', 'parent_seat_id', ...)
```

El campo `is_vacant` se calcula automáticamente:
```python
@api.depends('employee_id')
def _compute_is_vacant(self):
    for record in self:
        record.is_vacant = not bool(record.employee_id)
```

#### `EosPeopleEvaluation` — Evaluación GWC
**Tabla en BD:** `eos_people_evaluation`

Evalúa 3 dimensiones para determinar si una persona está en el asiento correcto:

```python
get_it          # ¿Entiende intuitivamente el puesto?
want_it         # ¿Genuinamente lo quiere?
capacity_to_do_it  # ¿Tiene tiempo, habilidades y energía?
shares_values   # ¿Comparte los valores fundamentales?
```

**Lógica de resultado automático:**
```python
@api.depends('get_it', 'want_it', 'capacity_to_do_it', 'shares_values')
def _compute_gwc_result(self):
    dims = [record.get_it, record.want_it, record.capacity_to_do_it]
    if not record.shares_values or 'no' in dims:
        record.gwc_result = 'wrong_seat'       # ❌ Asiento Incorrecto
    elif all(d == 'yes' for d in dims):
        record.gwc_result = 'right_seat'       # ✅ Asiento Correcto
    else:
        record.gwc_result = 'developing'       # 🔄 En Desarrollo
```

---

## 8. Componente 3 — DATOS

### Propósito en EOS

Eliminar la subjetividad de la gestión. Si no tienes números, no sabes si tu negocio está bien o mal. El Scorecard semanal da una foto instantánea de la salud del negocio.

### Modelos Python

#### `EosScorecard` — Tablero Semanal
**Archivo:** `models/eos_data.py`
**Tabla en BD:** `eos_scorecard`

Contenedor de 5-15 KPIs. Calcula automáticamente:
- `kpi_green_count` / `kpi_red_count` — cantidad de KPIs en cada estado
- `health_percentage` — porcentaje de KPIs en meta (objetivo EOS: ≥ 80%)

#### `EosKpi` — Indicador Clave de Rendimiento
**Tabla en BD:** `eos_kpi`

Calcula el estado semanal automáticamente:
```python
@api.depends('current_value', 'goal_value', 'goal_direction')
def _compute_weekly_status(self):
    if record.goal_direction == 'higher_is_better':
        # Verde si valor actual >= meta (ej: nuevos clientes)
        record.weekly_status = 'green' if record.current_value >= record.goal_value else 'red'
    else:
        # Verde si valor actual <= meta (ej: días de resolución de tickets)
        record.weekly_status = 'green' if record.current_value <= record.goal_value else 'red'
```

El método `action_log_weekly_record()` guarda el valor actual como registro histórico en `EosKpiRecord` y escribe un mensaje en el Chatter:
```python
self.env['eos.kpi.record'].create({...})
self.message_post(body=f'Registro Semanal W{week_number}/{year}...')
```

#### `EosOkr` + `EosOkrKeyResult` — OKRs
Los OKRs se vinculan con Rocas (`rock_id = Many2one('eos.vision.rock')`).

El progreso general del OKR es el promedio de sus Resultados Clave:
```python
@api.depends('key_result_ids.progress')
def _compute_overall_progress(self):
    record.overall_progress = sum(krs.mapped('progress')) / len(krs)
```

Cada `EosOkrKeyResult` calcula su propio progreso desde la línea base hasta el objetivo:
```python
delta_total = target_value - baseline_value
delta_current = current_value - baseline_value
progress = (delta_current / delta_total) * 100  # Porcentaje
```

---

## 9. Componente 4 — PROBLEMAS

### Propósito en EOS

Todo obstáculo, idea u oportunidad que impide alcanzar la visión es un "Issue". EOS propone el proceso **IDS** para resolverlos: Identificar → Discutir → Resolver.

### Modelo Python

#### `EosIssue` — Issue
**Archivo:** `models/eos_issues.py`
**Tabla en BD:** `eos_issue`

El formulario tiene 3 pestañas que corresponden exactamente a los pasos IDS:
- **Pestaña I:** `root_cause`, `impact`
- **Pestaña D:** `discussion_notes`, `discussed_in_meeting_id`
- **Pestaña S:** `solution`, `owner_id`, `date_resolution`

**Transiciones de estado:**
```python
def action_start_discussion(self):  # identified → discussing
def action_mark_solved(self):       # discussing → solved (requiere solution != False)
def action_drop(self):              # → dropped
def action_reopen(self):            # → identified
```

**Validación de negocio:** No se puede marcar como resuelto sin haber registrado la solución:
```python
def action_mark_solved(self):
    if not record.solution:
        raise ValidationError('Debe registrar la solución acordada...')
```

---

## 10. Componente 5 — PROCESOS

### Propósito en EOS

Documentar los 6-10 procesos críticos de la empresa de forma suficientemente clara para que cualquier persona con las habilidades correctas los ejecute de la misma manera.

### Modelos Python

#### `EosProcess` — Proceso Crítico
**Archivo:** `models/eos_processes.py`
**Tabla en BD:** `eos_process`

**Estados del proceso (ciclo de documentación EOS):**
```
draft → documented → followed ✅
            ↑___________|  (puede volver a "needs_update")
```

- `draft` = en construcción
- `documented` = escrito y aprobado por el dueño
- `followed` = el equipo lo ejecuta consistentemente
- `needs_update` = requiere revisión

#### `EosProcessStep` — Paso del Proceso
**Tabla en BD:** `eos_process_step`

Usa `sequence` con pasos de 10 en 10 (10, 20, 30...) para facilitar inserción de pasos intermedios sin reordenar todo.

El campo `attachment_ids = Many2many('ir.attachment')` permite adjuntar plantillas, formularios y guías directamente al paso.

---

## 11. Componente 6 — TRACCIÓN

### Propósito en EOS

La Tracción es la disciplina que convierte la Visión en resultados. Sus dos herramientas son la reunión L10 (90 minutos semanales con agenda fija) y los To-Dos (compromisos de 7 días).

### Modelos Python

#### `EosMeeting` — Reunión L10
**Archivo:** `models/eos_traction.py`
**Tabla en BD:** `eos_meeting`

El formulario implementa la agenda fija de 90 minutos con 7 pestañas:

| Pestaña | Tiempo | Campo(s) |
|---|---|---|
| 1. Check-In | 5 min | `checkin_notes` |
| 2. Scorecard | 5 min | `scorecard_id`, `scorecard_notes` |
| 3. Rocas | 5 min | `rocks_review_notes` |
| 4. Titulares | 5 min | `customer_headlines`, `employee_headlines` |
| 5. To-Dos | 5 min | `todo_ids` (tabla inline) |
| 6. IDS | 60 min | `issue_ids`, `ids_notes` |
| 7. Cierre | 5 min | `closing_notes`, `attendee_ids` (calificaciones) |

La calificación promedio se calcula automáticamente:
```python
@api.depends('attendee_ids.rating')
def _compute_rating_avg(self):
    rated = record.attendee_ids.filtered(lambda a: a.rating > 0)
    record.rating_avg = sum(rated.mapped('rating')) / len(rated)
```

#### `EosTodo` — Compromiso Semanal
**Tabla en BD:** `eos_todo`

El método más importante: `action_create_issue_from_todo()`. Implementa el ciclo EOS donde un To-Do no completado se convierte automáticamente en un Issue:

```python
def action_create_issue_from_todo(self):
    issue = self.env['eos.issue'].create({
        'name': f'[To-Do No Completado] {self.name}',
        'root_cause': f'To-Do "{self.name}" no fue completado antes del {self.date_due}.',
        ...
    })
    self.write({'related_issue_id': issue.id})
    # Abre el Issue recién creado
    return {'type': 'ir.actions.act_window', 'res_id': issue.id, ...}
```

---

## 12. Patrones Técnicos de Odoo 17 Usados en el Módulo

### `@api.depends` — Campos Calculados

```python
@api.depends('campo1', 'campo2.campo_relacionado')
def _compute_mi_campo(self):
    for record in self:
        record.mi_campo = ...  # siempre iterar con 'for record in self'
```

- Se ejecuta automáticamente cuando cambia cualquier campo listado.
- Con `store=True`: el valor se guarda en la BD (búsqueda más rápida, pero ocupa espacio).
- Sin `store=True`: se recalcula en cada visualización (más liviano, pero no buscable).

### `@api.onchange` — Reacción en Tiempo Real

```python
@api.onchange('date_deadline')
def _onchange_date_deadline(self):
    if self.date_deadline:
        self.quarter = 'q1' if self.date_deadline.month <= 3 else ...
```

- Se ejecuta en el navegador cuando el usuario cambia el campo. **No guarda en BD**.
- Sirve para UX: autocompletar campos relacionados.
- Diferencia clave con `@api.depends`: `onchange` es solo UI, `depends` es cálculo real.

### `@api.constrains` — Validaciones de Negocio

```python
@api.constrains('fecha_inicio', 'fecha_fin')
def _check_fechas(self):
    for record in self:
        if record.fecha_inicio > record.fecha_fin:
            raise ValidationError('La fecha de inicio no puede ser posterior...')
```

- Se ejecuta ANTES de guardar en la BD.
- Si lanza `ValidationError`, el registro no se guarda y el mensaje aparece al usuario.

### Visibilidad Condicional en Odoo 17 (nuevo atributo `invisible`)

En Odoo 17 se reemplazó `attrs={'invisible': [...]}` por expresiones directas:

```xml
<!-- Odoo 16 y anteriores (obsoleto) -->
<button attrs="{'invisible': [('state', '!=', 'draft')]}"/>

<!-- Odoo 17 (correcto) -->
<button invisible="state != 'draft'"/>
```

Este módulo usa la sintaxis de **Odoo 17** en todas las vistas.

### Relaciones entre Modelos

| Tipo | Uso | Ejemplo en el módulo |
|---|---|---|
| `Many2one` | N registros → 1 registro | `vision_id = Many2one('eos.vision')` en Rock |
| `One2many` | 1 registro → N registros | `annual_rocks_ids = One2many('eos.vision.rock', 'vision_id')` |
| `Many2many` | N registros ↔ N registros | `issue_ids = Many2many('eos.issue')` en Meeting |

### `ondelete='cascade'`

```python
vision_id = fields.Many2one('eos.vision', ondelete='cascade')
```

Si se elimina el V/TO padre, todas sus Rocas (`eos.vision.rock`) se eliminan automáticamente. Sin `cascade`, Odoo lanza un error al intentar eliminar un registro con hijos.

---

## 13. Guía de Uso Operativo para TLP Holding

### Configuración Inicial (una sola vez)

1. **Asignar roles** a todos los usuarios del equipo directivo (rol: Directivo)
2. **Crear el V/TO maestro** en *EOS → 1. Visión → V/TO*
3. **Construir el Accountability Chart** en *EOS → 2. Personas → Accountability Chart*
4. **Crear el Scorecard** en *EOS → 3. Datos → Scorecard Semanal* con los 5-15 KPIs iniciales

### Ciclo Semanal (cada lunes o el día definido)

| Paso | Responsable | Herramienta | Tiempo |
|---|---|---|---|
| Actualizar KPIs del Scorecard | Cada dueño de KPI | Scorecard → actualizar "Valor Esta Semana" | 5 min |
| Celebrar la L10 Meeting | Facilitador | *Tracción → Reuniones L10* → crear nueva | 90 min |
| Crear To-Dos de la reunión | Todos | En la pestaña To-Dos de la reunión | Durante la reunión |
| Actualizar estado de Rocas | Cada dueño | *Visión → Rocas* | 2 min |

### Ciclo Trimestral (cada 90 días)

1. Revisar y aprobar el V/TO para el nuevo trimestre
2. Definir las nuevas Rocas en la pestaña "Plan Anual y Rocas"
3. Crear OKRs alineados con las Rocas en *Datos → OKRs*
4. Aplicar la Puntuación de Visión a todo el equipo directivo
5. Realizar evaluaciones GWC si hay cambios en el equipo

### Interpretación de Indicadores

| Indicador | Objetivo EOS | Señal de Alerta |
|---|---|---|
| Puntuación de Visión | ≥ 80% | < 60%: reunión urgente de alineación |
| KPIs en Meta (Scorecard) | ≥ 80% verde | < 60%: revisar objetivos o estrategia |
| To-Dos completados | ≥ 80% | < 70%: problema de compromisos o capacidad |
| Rocas On Track | ≥ 80% | < 60%: revisar recursos y prioridades |
| Calificación L10 Meeting | ≥ 8/10 | < 7: mejorar la facilitación y agenda |

---

## 14. Solución de Problemas Comunes

### Error al instalar: "External ID not found"

**Causa:** Un archivo XML referencia un ID que no existe todavía (problema de orden de carga).
**Solución:** Verificar que en `__manifest__.py`, `security/eos_security.xml` aparece ANTES que cualquier vista XML.

### Error: "Model does not exist"

**Causa:** Un modelo referenciado en `ir.model.access.csv` no coincide con `_name` en Python.
**Regla:** El ID en el CSV usa guiones bajos: `model_eos_vision` = modelo `eos.vision`.

### La vista no muestra un campo

**Causa:** El campo no está en la lista de permisos del grupo del usuario.
**Solución:** Verificar `ir.model.access.csv` y el grupo asignado al usuario.

### `@api.onchange` no se dispara

**Causa:** El campo que cambia no está declarado en el decorador.
**Solución:** Agregar el campo al decorador: `@api.onchange('campo_que_activa')`.

### Campos `compute` no se actualizan

**Causa:** Falta `store=True` o el campo de dependencia no está en `@api.depends`.
**Solución:** Agregar todos los campos que afectan el cálculo al `@api.depends(...)`.

---

## 15. Glosario EOS y Técnico

### Términos EOS

| Término | Definición |
|---|---|
| **EOS** | Entrepreneurial Operating System. Sistema de gestión de 6 componentes. |
| **V/TO** | Vision/Traction Organizer. Documento estratégico central de EOS. |
| **BHAG** | Big Hairy Audacious Goal. Objetivo grande, osado y audaz a 10 años. |
| **Roca** | Prioridad estratégica de 90 días con un único dueño. |
| **GWC** | Get it / Want it / Capacity to do it. Evaluación de ajuste persona-puesto. |
| **IDS** | Identify / Discuss / Solve. Proceso de resolución de problemas de EOS. |
| **L10 Meeting** | Level 10 Meeting. Reunión semanal de 90 minutos del Leadership Team. |
| **Scorecard** | Tablero de 5-15 indicadores semanales de salud del negocio. |
| **Accountability Chart** | Mapa de responsabilidades (reemplaza al organigrama en EOS). |
| **Seat** | Asiento en el Accountability Chart: posición con funciones y dueño. |
| **To-Do** | Compromiso de 7 días con dueño único, revisado en cada L10. |
| **Leadership Team (LT)** | Equipo directivo responsable de ejecutar EOS. |
| **OKR** | Objective and Key Results. Objetivo + métricas de cumplimiento. |
| **KPI** | Key Performance Indicator. Indicador del Scorecard semanal. |

### Términos Técnicos Odoo

| Término | Definición |
|---|---|
| **Modelo** | Clase Python que define la estructura de datos (tabla en PostgreSQL). |
| **ORM** | Object-Relational Mapper. Permite operar la BD con Python sin SQL. |
| **Chatter** | Panel de mensajes y actividades en formularios Odoo (`mail.thread`). |
| **Manifest** | `__manifest__.py`. Archivo de metadatos del módulo. |
| **Many2one** | Campo de relación N→1. Guarda el ID del registro relacionado. |
| **One2many** | Campo de relación 1→N. Campo virtual, no crea columna en BD. |
| **Many2many** | Campo de relación N↔N. Crea tabla intermedia en BD. |
| **compute** | Campo calculado dinámicamente. Puede o no guardarse (`store=True`). |
| **tracking** | `tracking=True` en un campo: registra cambios en el Chatter. |
| **domain** | Filtro de búsqueda en formato lista: `[('state', '=', 'draft')]`. |
| **context** | Diccionario de contexto que pasa parámetros entre vistas y métodos. |
| **ir.model.access.csv** | Archivo de permisos CRUD por modelo y grupo de usuarios. |
| **addon/addons** | Módulo o carpeta de módulos de Odoo. Sinónimo de "módulo personalizado". |
| **DXA** | Unidad de medida usada en documentos Word (1440 DXA = 1 pulgada). |

---

*Manual Técnico — EOS Center Data v17.0.4.0.0*
*Universidad El Bosque — Ingeniería de Sistemas — 2025*
*Proyecto de Grado: Desarrollo Tecnológico*
