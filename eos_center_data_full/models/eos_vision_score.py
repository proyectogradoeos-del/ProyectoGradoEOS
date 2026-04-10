# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EosVisionScore(models.Model):
    """
    PUNTUACIÓN DE VISIÓN — Herramienta de evaluación del componente VISIÓN.

    En EOS, la "Puntuación de Visión" (Vision Score) es una encuesta
    que se aplica periódicamente al equipo de liderazgo para medir
    qué tan bien cada miembro "comparte, comprende y apoya" la visión
    de la empresa.

    Metodología:
    -----------
    Se evalúan 8 preguntas (una por cada sección del V/TO) en una
    escala del 1 al 10. El objetivo es que el equipo alcance un
    promedio superior al 80%.

    Si algún miembro puntúa por debajo de 7 en cualquier pregunta,
    se abre una conversación de alineación.
    """

    _name = 'eos.vision.score'
    _description = 'EOS - Puntuación de Visión'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, vision_id'
    _rec_name = 'display_name'

    # ---------------------------------------------------------------
    # Campos de identificación
    # ---------------------------------------------------------------
    vision_id = fields.Many2one(
        comodel_name='eos.vision',
        string='V/TO Evaluado',
        required=True,
        ondelete='cascade',
        tracking=True,
    )

    evaluator_id = fields.Many2one(
        comodel_name='res.users',
        string='Evaluador',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        help='Miembro del equipo de liderazgo que realiza la puntuación.',
    )

    date = fields.Date(
        string='Fecha de Evaluación',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('done', 'Completada'),
        ],
        string='Estado',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )

    # ---------------------------------------------------------------
    # PREGUNTAS DE PUNTUACIÓN (1-10)
    # Cada pregunta corresponde a una sección del V/TO
    # ---------------------------------------------------------------
    SCORE_SELECTION = [(str(i), str(i)) for i in range(11)]

    score_core_values = fields.Selection(
        selection=SCORE_SELECTION,
        string='1. Valores Fundamentales (1-10)',
        default='0',
        help='¿Qué tan claramente conoces y vives los valores '
             'fundamentales de la empresa?',
    )

    score_core_focus = fields.Selection(
        selection=SCORE_SELECTION,
        string='2. Enfoque Central / Propósito (1-10)',
        default='0',
        help='¿Qué tan claro tienes el propósito y nicho de la empresa?',
    )

    score_10_year = fields.Selection(
        selection=SCORE_SELECTION,
        string='3. Objetivo a 10 Años (1-10)',
        default='0',
        help='¿Qué tan alineado estás con el objetivo de largo plazo '
             'de la empresa?',
    )

    score_marketing = fields.Selection(
        selection=SCORE_SELECTION,
        string='4. Estrategia de Marketing (1-10)',
        default='0',
        help='¿Qué tan bien conoces y puedes comunicar la estrategia '
             'de mercado de la empresa?',
    )

    score_3_year = fields.Selection(
        selection=SCORE_SELECTION,
        string='5. Objetivos a 3 Años (1-10)',
        default='0',
        help='¿Qué tan claro tienes el plan y metas a 3 años?',
    )

    score_1_year = fields.Selection(
        selection=SCORE_SELECTION,
        string='6. Plan Anual (1-10)',
        default='0',
        help='¿Qué tan claro tienes las prioridades y metas del año?',
    )

    score_rocks = fields.Selection(
        selection=SCORE_SELECTION,
        string='7. Rocas del Trimestre (1-10)',
        default='0',
        help='¿Qué tan comprometido estás con las Rocas actuales '
             'del equipo?',
    )

    score_issues = fields.Selection(
        selection=SCORE_SELECTION,
        string='8. Claridad en Issues (1-10)',
        default='0',
        help='¿Qué tan bien se están resolviendo los problemas '
             'que bloquean la ejecución de la visión?',
    )

    # ---------------------------------------------------------------
    # CAMPOS CALCULADOS
    # ---------------------------------------------------------------
    score_total = fields.Integer(
        string='Puntuación Total',
        compute='_compute_scores',
        store=True,
        help='Suma total de las 8 preguntas (máximo: 80 puntos).',
    )

    score_percentage = fields.Float(
        string='Puntuación (%)',
        compute='_compute_scores',
        store=True,
        help='Porcentaje sobre el máximo posible (80 puntos = 100%). '
             'Objetivo EOS: ≥ 80%.',
    )

    alignment_level = fields.Selection(
        selection=[
            ('high', 'Alineado ✅ (≥80%)'),
            ('medium', 'En proceso ⚠️ (60-79%)'),
            ('low', 'Desalineado 🔴 (<60%)'),
        ],
        string='Nivel de Alineación',
        compute='_compute_scores',
        store=True,
    )

    display_name = fields.Char(
        string='Nombre',
        compute='_compute_display_name',
        store=True,
    )

    comments = fields.Text(
        string='Comentarios / Áreas de Mejora',
        help='Notas sobre qué puntos necesitan más trabajo de alineación.',
    )

    # ---------------------------------------------------------------
    # COMPUTE METHODS
    # ---------------------------------------------------------------
    @api.depends(
        'score_core_values', 'score_core_focus', 'score_10_year',
        'score_marketing', 'score_3_year', 'score_1_year',
        'score_rocks', 'score_issues',
    )
    def _compute_scores(self):
        """
        Calcula el total, porcentaje y nivel de alineación.
        Máximo posible: 8 preguntas × 10 puntos = 80 puntos.
        """
        for record in self:
            total = (
                int(record.score_core_values or '0')
                + int(record.score_core_focus or '0')
                + int(record.score_10_year or '0')
                + int(record.score_marketing or '0')
                + int(record.score_3_year or '0')
                + int(record.score_1_year or '0')
                + int(record.score_rocks or '0')
                + int(record.score_issues or '0')
            )
            record.score_total = total
            percentage = (total / 80.0) * 100 if total > 0 else 0.0
            record.score_percentage = round(percentage, 2)

            if percentage >= 80:
                record.alignment_level = 'high'
            elif percentage >= 60:
                record.alignment_level = 'medium'
            else:
                record.alignment_level = 'low'

    @api.depends('vision_id', 'evaluator_id', 'date')
    def _compute_display_name(self):
        for record in self:
            vision_name = record.vision_id.name or ''
            evaluator_name = record.evaluator_id.name or ''
            date_str = str(record.date) if record.date else ''
            record.display_name = f'Puntuación: {vision_name} | {evaluator_name} | {date_str}'

    # ---------------------------------------------------------------
    # CONSTRAINS — validar rango de puntajes
    # ---------------------------------------------------------------
    @api.constrains(
        'score_core_values', 'score_core_focus', 'score_10_year',
        'score_marketing', 'score_3_year', 'score_1_year',
        'score_rocks', 'score_issues',
    )
    def _check_scores_range(self):
        """Todos los puntajes deben estar entre 0 y 10."""
        score_fields = [
            'score_core_values', 'score_core_focus', 'score_10_year',
            'score_marketing', 'score_3_year', 'score_1_year',
            'score_rocks', 'score_issues',
        ]
        for record in self:
            for field_name in score_fields:
                value = int(getattr(record, field_name) or '0')
                if not (0 <= value <= 10):
                    raise ValidationError(
                        f'El puntaje "{field_name}" debe estar entre 0 y 10. '
                        f'Valor ingresado: {value}.'
                    )

    # ---------------------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------------------
    def action_submit(self):
        """Confirma la puntuación de visión."""
        for record in self:
            record.write({'state': 'done'})
