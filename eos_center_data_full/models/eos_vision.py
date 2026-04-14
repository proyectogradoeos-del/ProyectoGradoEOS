# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EosVision(models.Model):
    """
    Componente VISIÓN de la metodología EOS.

    Centraliza la Visión organizacional de TLP Holding a través del
    documento V/TO (Vision/Traction Organizer), que es la herramienta
    principal de EOS para definir y comunicar el rumbo estratégico
    de la empresa a todos los niveles.

    El V/TO se divide en dos partes:
      1. Visión    — ¿A dónde vamos? (valores, propósito, metas a 10/3/1 año)
      2. Tracción  — ¿Cómo llegamos? (Rocas trimestrales, indicadores)
                     (la parte de Tracción se implementa en el componente 6)
    """

    _name = 'eos.vision'
    _description = 'EOS - Visión Organizacional (V/TO)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'company_id, active desc, name'
    _rec_name = 'name'

    # ---------------------------------------------------------------
    # Campos de identificación
    # ---------------------------------------------------------------
    name = fields.Char(
        string='Nombre del V/TO',
        required=True,
        tracking=True,
        help='Nombre descriptivo para este documento de Visión/Tracción. '
             'Ejemplo: "V/TO 2025 - TLP Holding"',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
        help='Empresa del holding a la que pertenece esta Visión.',
    )

    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Los registros inactivos se archivan y no aparecen en las búsquedas normales.',
    )

    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de los V/TO en las listas y vistas.',
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('review', 'En Revisión'),
            ('approved', 'Aprobado'),
            ('archived', 'Archivado'),
        ],
        string='Estado',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
        help='Estado del ciclo de vida del documento V/TO.',
    )

    fiscal_year = fields.Char(
        string='Año Fiscal',
        tracking=True,
        help='Año fiscal al que corresponde este V/TO. Ejemplo: "2025".',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 1 — VALORES FUNDAMENTALES
    # ---------------------------------------------------------------
    core_values = fields.Text(
        string='Valores Fundamentales',
        tracking=True,
        help='Lista los valores fundamentales que guían la cultura y las '
             'decisiones de la organización. En EOS suelen ser 3 a 7 valores. '
             'Ejemplo:\n- Integridad\n- Innovación\n- Orientación al cliente',
    )

    core_focus_purpose = fields.Text(
        string='Propósito / Causa Central',
        tracking=True,
        help='¿Por qué existe la empresa? El "por qué" profundo más allá '
             'de ganar dinero. Ejemplo: "Acelerar la transformación digital '
             'de empresas en América Latina."',
    )

    core_focus_niche = fields.Text(
        string='Nicho (Lo que hacemos mejor)',
        tracking=True,
        help='El área específica en la que la empresa es o aspira a ser '
             'la mejor. Ejemplo: "Adquisición y gestión de empresas '
             'tecnológicas de alto crecimiento en LATAM."',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 2 — OBJETIVO A 10 AÑOS (BHAG / Meta a Largo Plazo)
    # ---------------------------------------------------------------
    goal_10_years = fields.Text(
        string='Objetivo a 10 Años (BHAG)',
        tracking=True,
        help='Big Hairy Audacious Goal — meta grande, osada y audaz para '
             'los próximos 10 años. Debe ser inspiradora y alcanzable. '
             'Ejemplo: "Ser el holding tecnológico líder en América Latina '
             'con 100 empresas gestionadas."',
    )

    marketing_strategy = fields.Text(
        string='Estrategia de Marketing (El Diferenciador)',
        tracking=True,
        help='¿Qué hace única a la empresa? ¿Cuál es su propuesta de valor '
             'diferenciadora en el mercado? Incluye el mercado objetivo, '
             'los 3 diferenciadores y el proceso de garantía.',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 3 — OBJETIVOS A 3 AÑOS
    # ---------------------------------------------------------------
    goal_3_years_date = fields.Date(
        string='Fecha Horizonte (3 años)',
        tracking=True,
        help='Fecha aproximada de cumplimiento de los objetivos a 3 años.',
    )

    goal_3_years_revenue = fields.Monetary(
        string='Ingresos Proyectados (3 años)',
        currency_field='currency_id',
        tracking=True,
        help='Meta de ingresos en moneda local para el horizonte de 3 años.',
    )

    goal_3_years_profit = fields.Monetary(
        string='Utilidad Proyectada (3 años)',
        currency_field='currency_id',
        tracking=True,
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )

    goal_3_years_measurables = fields.Text(
        string='Métricas Clave a 3 años',
        tracking=True,
        help='Listado de indicadores medibles que definen el éxito a 3 años. '
             'Formato sugerido:\n- Métrica 1: valor objetivo\n- Métrica 2: valor objetivo',
    )

    goal_3_years_description = fields.Text(
        string='Descripción del Estado Ideal a 3 años',
        tracking=True,
        help='Descripción narrativa de cómo se ve la empresa en 3 años: '
             'estructura, cultura, productos, mercado, etc.',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 4 — PLAN ANUAL (Prioridades del año / "Rocas" anuales)
    # ---------------------------------------------------------------
    goal_1_year_date = fields.Date(
        string='Fecha Horizonte (1 año)',
        tracking=True,
        help='Fecha de fin del año fiscal o período anual.',
    )

    goal_1_year_revenue = fields.Monetary(
        string='Ingresos Proyectados (1 año)',
        currency_field='currency_id',
        tracking=True,
    )

    goal_1_year_profit = fields.Monetary(
        string='Utilidad Proyectada (1 año)',
        currency_field='currency_id',
        tracking=True,
    )

    goal_1_year_measurables = fields.Text(
        string='Métricas Clave del Año',
        tracking=True,
        help='Indicadores y metas concretas para el año en curso.',
    )

    annual_rocks_ids = fields.One2many(
        comodel_name='eos.vision.rock',
        inverse_name='vision_id',
        string='Prioridades Anuales (Rocas)',
        help='Las 3 a 7 prioridades más importantes de la empresa para '
             'este año. En EOS se denominan "Rocas" por analogía con la '
             'teoría del frasco de Covey.',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 5 — ISSUES (Problemas a largo plazo de Visión)
    # ---------------------------------------------------------------
    vision_issues = fields.Text(
        string='Issues / Problemas de Visión',
        tracking=True,
        help='Lista de obstáculos o problemas identificados que podrían '
             'impedir alcanzar la visión. Estos se resuelven en el '
             'componente PROBLEMAS de EOS.',
    )

    # ---------------------------------------------------------------
    # CAMPOS DE AUDITORÍA Y CONTROL
    # ---------------------------------------------------------------
    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        default=lambda self: self.env.user,
        tracking=True,
        help='Usuario responsable de mantener actualizado este V/TO.',
    )

    last_review_date = fields.Date(
        string='Última Revisión',
        tracking=True,
        help='Fecha de la última revisión formal del V/TO (normalmente '
             'se revisa en las reuniones anuales o trimestrales del liderazgo).',
    )

    vision_score_ids = fields.One2many(
        comodel_name='eos.vision.score',
        inverse_name='vision_id',
        string='Puntuaciones de Visión',
    )

    vision_score_avg = fields.Float(
        string='Puntuación Promedio de Visión (%)',
        compute='_compute_vision_score_avg',
        store=True,
        help='Promedio de todas las puntuaciones de visión registradas. '
             'En EOS, un equipo "comparte y apoya" la visión cuando el '
             'promedio supera el 80%.',
    )

    notes = fields.Html(
        string='Notas Adicionales',
        help='Observaciones, contexto adicional o notas de reuniones.',
    )

    # ---------------------------------------------------------------
    # COMPUTE METHODS
    # ---------------------------------------------------------------
    @api.depends('vision_score_ids.score_percentage')
    def _compute_vision_score_avg(self):
        """
        Calcula el promedio de puntuación de visión.
        En EOS, la herramienta de puntuación de visión mide qué tan bien
        el equipo de liderazgo "comparte, comprende y apoya" la visión.
        Un resultado > 80% indica alineación saludable.
        """
        for record in self:
            scores = record.vision_score_ids.filtered(lambda s: s.state == 'done')
            if scores:
                record.vision_score_avg = sum(scores.mapped('score_percentage')) / len(scores)
            else:
                record.vision_score_avg = 0.0

    # ---------------------------------------------------------------
    # ONCHANGE
    # ---------------------------------------------------------------
    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Actualiza la moneda al cambiar la empresa."""
        if self.company_id:
            self.currency_id = self.company_id.currency_id

    # ---------------------------------------------------------------
    # CONSTRAINS
    # ---------------------------------------------------------------
    @api.constrains('goal_1_year_date', 'goal_3_years_date')
    def _check_dates(self):
        """Valida que la fecha de 3 años sea posterior a la de 1 año."""
        for record in self:
            if (record.goal_1_year_date and record.goal_3_years_date
                    and record.goal_1_year_date >= record.goal_3_years_date):
                raise ValidationError(
                    'La fecha horizonte a 3 años debe ser posterior '
                    'a la fecha horizonte a 1 año.'
                )

    # ---------------------------------------------------------------
    # ACTION METHODS (botones de estado)
    # ---------------------------------------------------------------
    def action_set_review(self):
        """Mueve el V/TO al estado 'En Revisión'."""
        for record in self:
            record.write({'state': 'review'})

    def action_approve(self):
        """Aprueba el V/TO y registra la fecha de revisión."""
        for record in self:
            record.write({
                'state': 'approved',
                'last_review_date': fields.Date.today(),
            })

    def action_set_draft(self):
        """Regresa el V/TO a borrador para edición."""
        for record in self:
            record.write({'state': 'draft'})

    def action_archive_vto(self):
        """Archiva el V/TO (ciclo cerrado)."""
        for record in self:
            record.write({'state': 'archived', 'active': False})

    # ---------------------------------------------------------------
    # SMART BUTTON — conteo de Rocas
    # ---------------------------------------------------------------
    def action_view_rocks(self):
        """Abre la lista de Rocas asociadas a esta Visión."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Rocas — {self.name}',
            'res_model': 'eos.vision.rock',
            'view_mode': 'list,form',
            'domain': [('vision_id', '=', self.id)],
            'context': {'default_vision_id': self.id},
        }


class EosVisionRock(models.Model):
    """
    ROCAS — Prioridades trimestrales/anuales del componente VISIÓN.

    En la metodología EOS, una "Roca" es un objetivo SMART de alta
    prioridad que debe completarse en 90 días (trimestre). Están
    inspiradas en la metáfora de Covey: si no pones las rocas grandes
    primero, no cabrán después.

    Cada Roca tiene:
    - Un dueño (owner) responsable de su cumplimiento.
    - Una fecha límite.
    - Un estado de seguimiento (on track / off track / done).
    """

    _name = 'eos.vision.rock'
    _description = 'EOS - Roca (Prioridad Estratégica)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'vision_id, sequence, name'

    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de importancia dentro del V/TO.',
    )

    name = fields.Char(
        string='Nombre de la Roca',
        required=True,
        tracking=True,
        help='Descripción concisa y clara del objetivo. '
             'Debe ser específico, medible y alcanzable en el período.',
    )

    vision_id = fields.Many2one(
        comodel_name='eos.vision',
        string='V/TO Asociado',
        required=True,
        ondelete='cascade',
        tracking=True,
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        related='vision_id.company_id',
        store=True,
        readonly=True,
    )

    owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Dueño (Owner)',
        required=True,
        tracking=True,
        help='Persona responsable de entregar esta Roca. '
             'En EOS, cada Roca tiene UN solo dueño.',
    )

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Área / Departamento',
        tracking=True,
        help='Área de la empresa a la que pertenece esta Roca.',
    )

    rock_type = fields.Selection(
        selection=[
            ('company', 'Roca de Empresa'),
            ('department', 'Roca de Área'),
            ('individual', 'Roca Individual'),
        ],
        string='Tipo de Roca',
        default='company',
        required=True,
        tracking=True,
        help='Nivel jerárquico de la Roca:\n'
             '- Empresa: prioridad de toda la organización.\n'
             '- Área: prioridad de un departamento.\n'
             '- Individual: prioridad personal de un colaborador.',
    )

    parent_id = fields.Many2one(
        comodel_name='eos.vision.rock',
        string='Roca Padre',
        index=True,
        help='Permite conectar esta roca a una roca de nivel superior (Empresa o Área).',
    )

    child_ids = fields.One2many(
        comodel_name='eos.vision.rock',
        inverse_name='parent_id',
        string='Rocas Hijas / Alineadas',
    )

    state = fields.Selection(
        selection=[
            ('on_track', 'En Camino ✅'),
            ('off_track', 'Fuera de Camino ⚠️'),
            ('done', 'Completada ✔'),
            ('not_started', 'No Iniciada'),
            ('cancelled', 'Cancelada'),
        ],
        string='Estado',
        default='not_started',
        required=True,
        tracking=True,
        copy=False,
    )

    date_start = fields.Date(
        string='Fecha de Inicio',
        tracking=True,
    )

    date_deadline = fields.Date(
        string='Fecha Límite',
        required=True,
        tracking=True,
        help='Fecha máxima de entrega. En EOS es generalmente el último '
             'día del trimestre en curso.',
    )

    quarter = fields.Selection(
        selection=[
            ('q1', 'Q1 (Ene-Mar)'),
            ('q2', 'Q2 (Abr-Jun)'),
            ('q3', 'Q3 (Jul-Sep)'),
            ('q4', 'Q4 (Oct-Dic)'),
        ],
        string='Trimestre',
        tracking=True,
        help='Trimestre al que pertenece esta Roca.',
    )

    description = fields.Text(
        string='Descripción / Criterios de Éxito',
        help='Detalle de la Roca y cómo se medirá su éxito al completarla. '
             'Se recomienda incluir criterios SMART.',
    )

    progress = fields.Integer(
        string='Avance (%)',
        default=0,
        tracking=True,
        help='Porcentaje de avance de la Roca (0-100).',
    )

    notes = fields.Text(
        string='Notas de Seguimiento',
        help='Observaciones del último check-in o reunión de seguimiento.',
    )

    # ---------------------------------------------------------------
    # CONSTRAINS
    # ---------------------------------------------------------------
    @api.constrains('progress')
    def _check_progress(self):
        for record in self:
            if not (0 <= record.progress <= 100):
                raise ValidationError('El avance debe ser un valor entre 0 y 100%.')

    @api.constrains('date_start', 'date_deadline')
    def _check_dates(self):
        for record in self:
            if (record.date_start and record.date_deadline
                    and record.date_start > record.date_deadline):
                raise ValidationError(
                    'La fecha de inicio no puede ser posterior a la fecha límite.'
                )

    # ---------------------------------------------------------------
    # ONCHANGE — auto-completar trimestre
    # ---------------------------------------------------------------
    @api.onchange('date_deadline')
    def _onchange_date_deadline(self):
        """Infiere el trimestre a partir de la fecha límite."""
        if self.date_deadline:
            month = self.date_deadline.month
            if month <= 3:
                self.quarter = 'q1'
            elif month <= 6:
                self.quarter = 'q2'
            elif month <= 9:
                self.quarter = 'q3'
            else:
                self.quarter = 'q4'

    # ---------------------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------------------
    def action_mark_done(self):
        """Marca la Roca como completada al 100%."""
        for record in self:
            record.write({'state': 'done', 'progress': 100})

    def action_mark_off_track(self):
        for record in self:
            record.write({'state': 'off_track'})

    def action_mark_on_track(self):
        for record in self:
            record.write({'state': 'on_track'})
