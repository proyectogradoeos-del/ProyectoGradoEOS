# -*- coding: utf-8 -*-
"""
COMPONENTE 4 — PROBLEMAS (Issues)
===================================
En EOS, "Problemas" no es un término negativo: es todo obstáculo, idea,
oportunidad o fricción que impide que la empresa alcance su visión.
EOS propone un proceso específico para resolverlos: IDS.

PROCESO IDS (Identify – Discuss – Solve):
  1. IDENTIFICAR (I): Nombrar el problema real, no el síntoma.
     La habilidad es distinguir el problema raíz del síntoma visible.
  2. DISCUTIR (D): Abrir debate hasta que todos entiendan el problema.
     Solo se discute UN problema a la vez.
  3. RESOLVER (S): Tomar una decisión y asignar quién la ejecuta.
     Las soluciones deben ser concretas y con responsable.

La herramienta es la Lista de Issues (Issues List), que se revisa en
cada reunión L10 (Level 10 Meeting).

TIPOS DE ISSUES EN EOS:
  - Issues de corto plazo: se resuelven en la reunión semanal (L10)
  - Issues de largo plazo ("estacionales"): van al V/TO como obstáculos estratégicos

Modelos:
  - EosIssue: Issue individual con proceso IDS
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EosIssue(models.Model):
    """
    ISSUE — Problema, obstáculo u oportunidad identificado en EOS.

    Cada Issue sigue el proceso IDS de EOS:
    1. Se identifica con claridad (qué es, cuál es la causa raíz)
    2. Se discute en reunión (L10 Meeting o sesión estratégica)
    3. Se resuelve con una decisión concreta y un responsable de ejecución

    Un Issue mal resuelto en EOS es aquel que:
    - Nunca se cierra (se arrastra semana a semana)
    - Tiene responsable pero sin fecha de resolución
    - Se trató el síntoma en vez del problema raíz

    En la BD: eos_issue
    """

    _name = 'eos.issue'
    _description = 'EOS - Issue (Problema / Obstáculo / Oportunidad)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_identified desc'

    # ---------------------------------------------------------------
    # Identificación del Issue
    # ---------------------------------------------------------------
    name = fields.Char(
        string='Título del Issue',
        required=True,
        tracking=True,
        help='Descripción corta y clara del issue. Debe identificar el PROBLEMA '
             'RAÍZ, no el síntoma. Ej: "El proceso de onboarding de clientes '
             'tarda 3 semanas en vez de 1" (síntoma identificado correctamente).',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )

    identified_by = fields.Many2one(
        comodel_name='res.users',
        string='Identificado por',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )

    date_identified = fields.Date(
        string='Fecha de Identificación',
        default=fields.Date.today,
        required=True,
    )

    issue_type = fields.Selection(
        selection=[
            ('short_term', 'Corto Plazo (Reunión L10)'),
            ('long_term', 'Largo Plazo (Estratégico / V/TO)'),
            ('opportunity', 'Oportunidad'),
        ],
        string='Tipo de Issue',
        default='short_term',
        required=True,
        tracking=True,
        help='Corto plazo: se resuelve en la reunión semanal L10.\n'
             'Largo plazo: obstáculo estratégico que va al V/TO.\n'
             'Oportunidad: idea o mejora posible.',
    )

    priority = fields.Selection(
        selection=[
            ('0', 'Normal'),
            ('1', 'Alta ⭐'),
            ('2', 'Crítica ⭐⭐'),
        ],
        string='Prioridad',
        default='0',
        tracking=True,
    )

    # ---------------------------------------------------------------
    # Paso I — IDENTIFICAR
    # ---------------------------------------------------------------
    root_cause = fields.Text(
        string='Causa Raíz (I — Identificar)',
        tracking=True,
        help='Descripción del problema real detrás del síntoma visible. '
             'Usar "5 Porqués" u otra técnica de análisis de causa raíz. '
             'Responder: ¿Por qué está ocurriendo esto realmente?',
    )

    impact = fields.Text(
        string='Impacto si no se resuelve',
        help='¿Qué consecuencias tiene no resolver este issue? '
             'Cuantificar cuando sea posible.',
    )

    # ---------------------------------------------------------------
    # Paso D — DISCUTIR
    # ---------------------------------------------------------------
    discussion_notes = fields.Text(
        string='Notas de Discusión (D — Discutir)',
        tracking=True,
        help='Resumen de la discusión del equipo sobre este issue. '
             '¿Qué perspectivas surgieron? ¿Qué se descubrió al debatirlo?',
    )

    discussed_in_meeting_id = fields.Many2one(
        comodel_name='eos.meeting',
        string='Discutido en la Reunión',
        tracking=True,
        help='Reunión L10 en la que se discutió este issue.',
    )

    date_discussed = fields.Date(
        string='Fecha de Discusión',
        tracking=True,
    )

    # ---------------------------------------------------------------
    # Paso S — RESOLVER
    # ---------------------------------------------------------------
    solution = fields.Text(
        string='Solución Acordada (S — Resolver)',
        tracking=True,
        help='Decisión concreta tomada por el equipo para resolver el issue. '
             'Debe ser específica y accionable.',
    )

    owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable de la Solución',
        tracking=True,
        help='Persona responsable de ejecutar la solución acordada.',
    )

    date_resolution = fields.Date(
        string='Fecha Límite de Resolución',
        tracking=True,
    )

    date_resolved = fields.Date(
        string='Fecha Real de Resolución',
        tracking=True,
    )

    # ---------------------------------------------------------------
    # Estado del Issue
    # ---------------------------------------------------------------
    state = fields.Selection(
        selection=[
            ('identified', 'Identificado 🔍'),
            ('discussing', 'En Discusión 💬'),
            ('solved', 'Resuelto ✅'),
            ('dropped', 'Descartado 🗑️'),
        ],
        string='Estado IDS',
        default='identified',
        required=True,
        tracking=True,
        copy=False,
    )

    # ---------------------------------------------------------------
    # Categorización adicional
    # ---------------------------------------------------------------
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Área Relacionada',
        tracking=True,
    )

    related_rock_id = fields.Many2one(
        comodel_name='eos.vision.rock',
        string='Roca Relacionada',
        tracking=True,
        help='Si este issue bloquea el cumplimiento de una Roca específica.',
    )

    recurring = fields.Boolean(
        string='¿Es Recurrente?',
        tracking=True,
        help='Marcar si este issue ha aparecido más de una vez. '
             'Los issues recurrentes indican un problema sistémico que '
             'requiere solución estructural, no solo reactiva.',
    )

    # ---------------------------------------------------------------
    # CONSTRAINS
    # ---------------------------------------------------------------
    @api.constrains('date_resolution', 'date_identified')
    def _check_resolution_date(self):
        for record in self:
            if (record.date_resolution and record.date_identified
                    and record.date_resolution < record.date_identified):
                raise ValidationError(
                    'La fecha límite de resolución no puede ser anterior '
                    'a la fecha de identificación del issue.'
                )

    # ---------------------------------------------------------------
    # ACTIONS — Transiciones IDS
    # ---------------------------------------------------------------
    def action_start_discussion(self):
        """Mueve el Issue al paso D (Discutir) del proceso IDS."""
        for record in self:
            record.write({'state': 'discussing'})

    def action_mark_solved(self):
        """Marca el issue como resuelto y registra la fecha."""
        for record in self:
            if not record.solution:
                raise ValidationError(
                    'Debe registrar la solución acordada antes de marcar '
                    'el issue como resuelto.'
                )
            record.write({
                'state': 'solved',
                'date_resolved': fields.Date.today(),
            })

    def action_drop(self):
        """Descarta el issue (no es relevante o ya no aplica)."""
        for record in self:
            record.write({'state': 'dropped'})

    def action_reopen(self):
        """Reabre un issue cerrado."""
        for record in self:
            record.write({'state': 'identified', 'date_resolved': False})
