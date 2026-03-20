{
    "name": "EOS DATA",
    "summary": "Frontend de dashboard EOS DATA (Mi 90) — solo interfaz",
    "version": "1.1.0",
    "category": "Productivity",
    "author": "Tu Empresa",
    "website": "https://example.com",
    "license": "LGPL-3",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/eos_menu.xml",
        "data/ir_actions.xml",
        "views/eos_models_views.xml",
        "views/eos_issue_views.xml",
        "views/eos_meeting_views.xml",
        "views/eos_kpi_views.xml",
        "views/eos_todo_views.xml",
        "views/eos_key_result_views.xml",
        "data/ir_cron.xml",
    ],
    "demo": [
        "demo/demo_rocks.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "mi90_eos/static/src/css/dashboard.css",
            "mi90_eos/static/src/xml/dashboard.xml",
            "mi90_eos/static/src/xml/todos.xml",
            "mi90_eos/static/src/xml/scorecard.xml",
            "mi90_eos/static/src/xml/rocks.xml",
            "mi90_eos/static/src/xml/issues.xml",
            "mi90_eos/static/src/xml/meetings.xml",
            "mi90_eos/static/src/js/dashboard_action.js",
            "mi90_eos/static/src/js/todo_board.js",
        ]
    },
    "installable": True,
    "application": True
}
