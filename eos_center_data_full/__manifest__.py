# -*- coding: utf-8 -*-
{
    'name': 'EOS Center Data',
    'version': '17.0.4.0.0',
    'summary': 'Centralización de la metodología EOS para TLP Holding en Odoo 17',
    'description': """
EOS Center Data — Versión Completa (100%)
==========================================
Módulo para TLP Holding que digitaliza los 6 componentes EOS en Odoo 17.
Componentes: Visión, Personas, Datos, Problemas, Procesos, Tracción.
    """,
    'author': 'EOS Center Data Team - Universidad El Bosque',
    'website': 'https://www.tlp.group',
    'category': 'Management',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/eos_security.xml',
        'security/ir.model.access.csv',
        'data/eos_vision_data.xml',
        'views/eos_vision_views.xml',
        'views/eos_vision_score_views.xml',
        'views/eos_people_views.xml',
        'views/eos_data_views.xml',
        'views/eos_issues_views.xml',
        'views/eos_processes_views.xml',
        'views/eos_traction_views.xml',
        'views/eos_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'eos_center_data_full/static/src/css/eos_styles.css',
        ],
    },
    # 'images': ['static/description/icon.png'],  # Crear icono primero
    'installable': True,
    'application': True,
    'auto_install': False,
}
