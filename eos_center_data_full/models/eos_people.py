# -*- coding: utf-8 -*-
"""
COMPONENTE 2 — PERSONAS (People)
=================================
En EOS, el componente "Personas" se basa en dos preguntas fundamentales:
  1. ¿Tenemos a las personas correctas? (Right People)
     → Personas que comparten y viven los Valores Fundamentales de la empresa.
  2. ¿Están en los puestos correctos? (Right Seats)
     → Personas que "Entienden / Quieren / Tienen capacidad" (Get it / Want it / Capacity to do it).

La herramienta principal es el Accountability Chart (AC), que es diferente
a un organigrama clásico: cada "asiento" (Seat) tiene funciones específicas
y métricas de rendimiento claras, no solo una jerarquía.

Modelos de este archivo:
  - EosSeat: Un "asiento" en el Accountability Chart (posición con responsabilidades)
  - EosPeopleEvaluation: Evaluación GWC de una persona en un asiento
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EosSeat(models.Model):
    """
    ASIENTO (Seat) — Posición en el Accountability Chart de EOS.

    Un Seat NO es solo un cargo: es una posición con:
    - Funciones específicas y medibles (Roles)
    - Un único titular responsable (Accountability)
    - Métricas de éxito definidas

    El Accountability Chart tiene 3 funciones principales al nivel más alto:
    Visión/Traction (liderazgo), Mercadeo/Ventas, Operaciones/Finanzas/RR.HH.
    Bajo cada una se pueden anidar asientos de segundo y tercer nivel.

    En la BD se guarda como: eos_seat
    """

    _name = 'eos.seat'
    _description = 'EOS - Asiento del Accountability Chart'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _rec_name = 'name'

    # ---------------------------------------------------------------
    # Identificación y jerarquía del AC
    # ---------------------------------------------------------------
    name = fields.Char(
        string='Nombre del Asiento',
        required=True,
        tracking=True,
        help='Nombre del rol o posición. Ej: "Director de Operaciones", '
             '"Líder de Producto", "Integrador".',
    )

    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de aparición en el Accountability Chart.',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )

    parent_seat_id = fields.Many2one(
        comodel_name='eos.seat',
        string='Asiento Superior',
        ondelete='set null',
        tracking=True,
        help='El asiento al que reporta este puesto en el Accountability Chart. '
             'Si está vacío, es un asiento de nivel raíz (ej. Integrador/CEO).',
    )

    child_seat_ids = fields.One2many(
        comodel_name='eos.seat',
        inverse_name='parent_seat_id',
        string='Asientos Subordinados',
    )

    seat_level = fields.Selection(
        selection=[
            ('leadership', 'Liderazgo (Nivel 1)'),
            ('management', 'Gerencia (Nivel 2)'),
            ('operational', 'Operativo (Nivel 3)'),
        ],
        string='Nivel en el AC',
        default='management',
        required=True,
        tracking=True,
    )

    # ---------------------------------------------------------------
    # Titular del asiento
    # ---------------------------------------------------------------
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Titular del Asiento',
        tracking=True,
        help='Empleado que actualmente ocupa este asiento. '
             'En EOS, cada asiento tiene UN solo titular.',
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario en Odoo',
        related='employee_id.user_id',
        store=True,
        readonly=True,
    )

    is_vacant = fields.Boolean(
        string='Asiento Vacante',
        compute='_compute_is_vacant',
        store=True,
        help='Indica si el asiento no tiene un titular asignado.',
    )

    # ---------------------------------------------------------------
    # Roles y responsabilidades del asiento
    # ---------------------------------------------------------------
    primary_roles = fields.Text(
        string='Roles Principales (5 máx.)',
        tracking=True,
        help='Lista de las 5 responsabilidades principales de este asiento. '
             'En EOS cada asiento debe tener máximo 5 roles claramente definidos.\n'
             'Formato sugerido:\n1. Responsabilidad A\n2. Responsabilidad B',
    )

    key_metrics = fields.Text(
        string='Métricas Clave de Éxito',
        tracking=True,
        help='Indicadores que definen si el titular del asiento está '
             'cumpliendo exitosamente con sus roles.',
    )

    description = fields.Text(
        string='Descripción del Asiento',
        help='Contexto adicional, alcance del rol y expectativas.',
    )

    # ---------------------------------------------------------------
    # Evaluaciones GWC
    # ---------------------------------------------------------------
    evaluation_ids = fields.One2many(
        comodel_name='eos.people.evaluation',
        inverse_name='seat_id',
        string='Evaluaciones GWC',
    )

    latest_gwc_state = fields.Selection(
        selection=[
            ('right_seat', 'Asiento Correcto ✅'),
            ('wrong_seat', 'Asiento Incorrecto ❌'),
            ('developing', 'En Desarrollo 🔄'),
            ('not_evaluated', 'Sin Evaluar'),
        ],
        string='Estado GWC Actual',
        compute='_compute_latest_gwc',
        store=True,
    )

    # ---------------------------------------------------------------
    # COMPUTES
    # ---------------------------------------------------------------
    @api.depends('employee_id')
    def _compute_is_vacant(self):
        for record in self:
            record.is_vacant = not bool(record.employee_id)

    @api.depends('evaluation_ids.gwc_result', 'evaluation_ids.date')
    def _compute_latest_gwc(self):
        """Obtiene el resultado GWC de la evaluación más reciente."""
        for record in self:
            latest = record.evaluation_ids.sorted('date', reverse=True)[:1]
            if latest:
                record.latest_gwc_state = latest.gwc_result
            else:
                record.latest_gwc_state = 'not_evaluated'


class EosPeopleEvaluation(models.Model):
    """
    EVALUACIÓN GWC — Get it / Want it / Capacity to do it.

    Es la herramienta de EOS para evaluar si una persona está en el
    asiento correcto. Evalúa tres dimensiones:

    - GET IT (Lo entiende): ¿La persona comprende intuitivamente
      las responsabilidades, la cultura y el ritmo del puesto?

    - WANT IT (Lo quiere): ¿Genuinamente quiere este puesto,
      más allá de la compensación económica?

    - CAPACITY TO DO IT (Tiene capacidad): ¿Tiene el tiempo,
      conocimiento, habilidades y energía para desempeñarse bien?

    Si las tres respuestas son SÍ → Persona correcta en asiento correcto.
    Si alguna es NO → Se debe tener una conversación directa sobre el ajuste.

    En la BD: eos_people_evaluation
    """

    _name = 'eos.people.evaluation'
    _description = 'EOS - Evaluación GWC (Get it / Want it / Capacity)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    # ---------------------------------------------------------------
    # Cabecera
    # ---------------------------------------------------------------
    seat_id = fields.Many2one(
        comodel_name='eos.seat',
        string='Asiento Evaluado',
        required=True,
        ondelete='cascade',
        tracking=True,
    )

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Empleado Evaluado',
        required=True,
        tracking=True,
    )

    evaluator_id = fields.Many2one(
        comodel_name='res.users',
        string='Evaluador',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )

    date = fields.Date(
        string='Fecha de Evaluación',
        default=fields.Date.today,
        required=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        related='seat_id.company_id',
        store=True,
        readonly=True,
    )

    # ---------------------------------------------------------------
    # Las 3 dimensiones GWC
    # ---------------------------------------------------------------
    get_it = fields.Selection(
        selection=[('yes', 'Sí ✅'), ('no', 'No ❌'), ('partial', 'Parcial ⚠️')],
        string='¿Lo entiende? (Get It)',
        required=True,
        tracking=True,
        help='¿La persona comprende intuitivamente las responsabilidades, '
             'la cultura y el ritmo necesario para tener éxito en este puesto?',
    )

    want_it = fields.Selection(
        selection=[('yes', 'Sí ✅'), ('no', 'No ❌'), ('partial', 'Parcial ⚠️')],
        string='¿Lo quiere? (Want It)',
        required=True,
        tracking=True,
        help='¿La persona genuinamente desea asumir las responsabilidades '
             'de este puesto, más allá de la compensación?',
    )

    capacity_to_do_it = fields.Selection(
        selection=[('yes', 'Sí ✅'), ('no', 'No ❌'), ('partial', 'Parcial ⚠️')],
        string='¿Tiene capacidad? (Capacity to Do It)',
        required=True,
        tracking=True,
        help='¿Tiene el tiempo, conocimiento, habilidades emocionales y '
             'energía para desempeñarse exitosamente en este puesto?',
    )

    shares_values = fields.Boolean(
        string='¿Comparte los Valores Fundamentales?',
        default=True,
        tracking=True,
        help='¿La persona vive y representa los Valores Fundamentales '
             'de la empresa en su comportamiento diario?',
    )

    # ---------------------------------------------------------------
    # Resultado y notas
    # ---------------------------------------------------------------
    gwc_result = fields.Selection(
        selection=[
            ('right_seat', 'Asiento Correcto ✅'),
            ('wrong_seat', 'Asiento Incorrecto ❌'),
            ('developing', 'En Desarrollo 🔄'),
        ],
        string='Resultado GWC',
        compute='_compute_gwc_result',
        store=True,
        tracking=True,
    )

    notes = fields.Text(
        string='Notas y Plan de Acción',
        help='Observaciones de la evaluación y pasos concretos '
             'acordados para mejorar el desempeño o ajustar el asiento.',
    )

    # ---------------------------------------------------------------
    # COMPUTE — Resultado automático
    # ---------------------------------------------------------------
    @api.depends('get_it', 'want_it', 'capacity_to_do_it', 'shares_values')
    def _compute_gwc_result(self):
        """
        Lógica de resultado GWC:
        - Asiento Correcto: Las 3 dimensiones son 'yes' Y comparte valores.
        - En Desarrollo: Al menos una dimensión es 'partial' y no hay 'no'.
        - Asiento Incorrecto: Cualquier dimensión es 'no' o no comparte valores.
        """
        for record in self:
            dims = [record.get_it, record.want_it, record.capacity_to_do_it]
            if not record.shares_values or 'no' in dims:
                record.gwc_result = 'wrong_seat'
            elif all(d == 'yes' for d in dims):
                record.gwc_result = 'right_seat'
            else:
                record.gwc_result = 'developing'
