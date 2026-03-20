# Mi 90 EOS Dashboard - Módulo Odoo

Este módulo proporciona un dashboard completo para la implementación del Sistema Operativo Empresarial (EOS) en Odoo.

## Características

- **Mi 90**: Dashboard principal con métricas y KPIs
- **Scorecard**: Seguimiento de métricas clave
- **Rocas**: Gestión de objetivos trimestrales
- **To-Dos**: Lista de tareas del equipo
- **Problemas**: Gestión de issues y obstáculos
- **Reuniones**: Calendario de reuniones EOS
- **Titulares**: Noticias y comunicaciones
- **V/TO®**: Visión, Tracción, Organización
- **Organigrama de Responsabilidades**: Estructura organizacional
- **1-a-1**: Reuniones individuales
- **Proceso**: Documentación de procesos
- **Directorio**: Contactos del equipo
- **EOS Toolbox™**: Herramientas adicionales

## Instalación

1. Copia el módulo a tu directorio de addons de Odoo:
   ```
   C:\mi_odoo_addons\mi90_eos\
   ```

2. Actualiza la lista de módulos en Odoo:
   - Ve a Apps > Actualizar lista de aplicaciones

3. Instala el módulo:
   - Busca "Mi 90 EOS Dashboard"
   - Haz clic en "Instalar"

## Uso

Una vez instalado, encontrarás el menú "EOS Dashboard" en la interfaz principal de Odoo. Desde ahí podrás acceder a todas las funcionalidades del sistema EOS.

## Estructura del módulo

```
mi90_eos/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── models/
│   ├── __init__.py
│   └── eos_dashboard.py
├── views/
│   ├── eos_dashboard_views.xml
│   └── eos_menu.xml
├── security/
│   └── ir.model.access.csv
└── static/
    └── src/
        ├── css/
        │   └── styles.css
        └── js/
            └── app.js
```

## Desarrollo

Este módulo está basado en el prototipo estático original y adaptado para funcionar como un módulo completo de Odoo con:

- Controladores HTTP para manejar las rutas
- Plantillas QWeb para renderizar las vistas
- Archivos estáticos (CSS/JS) integrados
- Menús y acciones configurados
- Modelos de datos básicos

## Soporte

Para soporte técnico o consultas sobre el módulo, contacta al desarrollador.
