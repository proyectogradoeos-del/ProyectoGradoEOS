# -*- coding: utf-8 -*-
"""
COMPONENTE 3 — DATOS (Data)
============================
En EOS, el componente "Datos" propone eliminar la subjetividad de la gestión
empresarial y reemplazarla por números. La herramienta clave es el Scorecard
(marcador), una tabla de 5-15 indicadores semanales que muestran la salud
del negocio en tiempo real.

Principio fundamental:
  "Los números dan claridad, detectan problemas antes de que se vuelvan crisis,
   y eliminan las conversaciones subjetivas sobre 'cómo van las cosas'."

Este módulo implementa dos sub-herramientas:
  1. Scorecard EOS: Tablero semanal de KPIs con responsables
  2. OKRs: Objetivos y Resultados Clave vinculados a las Rocas de Visión

Modelos de este archivo:
  - EosScorecard: El marcador semanal (contenedor de indicadores)
  - EosKpi: Indicador individual con metas y registros históricos
  - EosKpiRecord: Registro semanal de un KPI
  - EosOkr: Objetivo y Resultados Clave
  - EosOkrKeyResult: Resultado Clave individual de un OKR
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime


class EosScorecard(models.Model):
    """
    SCORECARD — Tablero de indicadores semanales EOS.

    El Scorecard es una hoja simple con 5-15 números que cualquier
    líder puede revisar en 5 minutos y saber inmediatamente si el
    negocio está "en camino" (verde) o "fuera de camino" (rojo).

    Cada KPI del Scorecard tiene:
    - Un responsable (owner) — no el que ejecuta, sino quien rinde cuentas
    - Una meta semanal
    - Un valor real de esa semana
    - Un estado: verde (≥ meta) o rojo (< meta)

    En la BD: eos_scorecard
    """

    _name = 'eos.scorecard'
    _description = 'EOS - Scorecard Semanal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'company_id, name'

    name = fields.Char(
        string='Nombre del Scorecard',
        required=True,
        tracking=True,
        help='Ej: "Scorecard Semanal TLP Holding 2025"',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )

    state = fields.Selection(
        selection=[('active', 'Activo'), ('closed', 'Cerrado')],
        string='Estado',
        default='active',
        tracking=True,
    )

    week_number = fields.Char(
        string='Semana',
        default=lambda self: str(datetime.date.today().isocalendar()[1]),
        tracking=True,
    )

    year = fields.Char(
        string='Año',
        default=lambda self: str(datetime.date.today().year),
        tracking=True,
    )

    active = fields.Boolean(default=True)

    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable del Scorecard',
        default=lambda self: self.env.user,
        tracking=True,
        help='Usuario que mantiene actualizado el Scorecard.',
    )

    kpi_ids = fields.One2many(
        comodel_name='eos.kpi',
        inverse_name='scorecard_id',
        string='Indicadores (KPIs)',
    )

    kpi_count = fields.Integer(
        string='# KPIs',
        compute='_compute_kpi_stats',
        store=True,
    )

    kpi_green_count = fields.Integer(
        string='KPIs en Verde',
        compute='_compute_kpi_stats',
        store=True,
    )

    kpi_red_count = fields.Integer(
        string='KPIs en Rojo',
        compute='_compute_kpi_stats',
        store=True,
    )

    health_percentage = fields.Float(
        string='Salud del Scorecard (%)',
        compute='_compute_kpi_stats',
        store=True,
        help='Porcentaje de KPIs en verde esta semana. Objetivo EOS: ≥ 80%.',
    )

    notes = fields.Text(string='Notas de la Semana')

    @api.depends('kpi_ids.weekly_status')
    def _compute_kpi_stats(self):
        for record in self:
            kpis = record.kpi_ids
            total = len(kpis)
            green = len(kpis.filtered(lambda k: k.weekly_status == 'green'))
            red = len(kpis.filtered(lambda k: k.weekly_status == 'red'))
            record.kpi_count = total
            record.kpi_green_count = green
            record.kpi_red_count = red
            record.health_percentage = (green / total * 100) if total > 0 else 0.0

    def action_view_kpis(self):
        self.ensure_one()
        return {
            'name': 'KPIs',
            'type': 'ir.actions.act_window',
            'res_model': 'eos.kpi',
            'view_mode': 'list,form',
            'domain': [('scorecard_id', '=', self.id)],
            'context': {'default_scorecard_id': self.id},
        }

    def action_rollover_next_week(self):
        """
        Cierra el Scorecard actual y genera uno nuevo para la siguiente semana.
        Copia todos los KPIs poniendolos a 0 en el valor real.
        """
        for record in self:
            next_week = int(record.week_number) + 1
            next_year = int(record.year)
            if next_week > 52:
                next_week = 1
                next_year += 1

            new_scorecard = record.copy({
                'state': 'active',
                'week_number': str(next_week),
                'year': str(next_year),
                'kpi_ids': False,
            })

            for kpi in record.kpi_ids:
                kpi.copy({
                    'scorecard_id': new_scorecard.id,
                    'current_value': 0.0,
                })

            record.write({'state': 'closed'})
            
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class EosKpi(models.Model):
    """
    KPI — Indicador Clave de Rendimiento del Scorecard EOS.

    Cada KPI representa una métrica que se registra semanalmente.
    Tiene una meta definida y genera una alerta visual (verde/rojo)
    automáticamente según si se cumplió o no.

    En la BD: eos_kpi
    """

    _name = 'eos.kpi'
    _description = 'EOS - KPI (Indicador Clave de Rendimiento)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scorecard_id, sequence'

    sequence = fields.Integer(default=10)

    name = fields.Char(
        string='Nombre del Indicador',
        required=True,
        tracking=True,
        help='Ej: "Nuevos clientes contactados", "Tickets resueltos", "MRR".',
    )

    scorecard_id = fields.Many2one(
        comodel_name='eos.scorecard',
        string='Scorecard',
        required=True,
        ondelete='cascade',
        tracking=True,
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        related='scorecard_id.company_id',
        store=True,
        readonly=True,
    )

    owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable (Owner)',
        required=True,
        tracking=True,
        help='Persona que rinde cuentas por este número cada semana.',
    )

    kpi_type = fields.Selection(
        selection=[
            ('number', 'Número'),
            ('percentage', 'Porcentaje (%)'),
            ('currency', 'Monetario ($)'),
            ('boolean', 'Sí/No'),
        ],
        string='Tipo de Métrica',
        default='number',
        required=True,
    )

    goal_value = fields.Float(
        string='Meta Semanal',
        required=True,
        tracking=True,
        help='Valor objetivo para cada semana. '
             'El KPI se marcará verde si el valor real es ≥ a este.',
    )

    goal_direction = fields.Selection(
        selection=[
            ('higher_is_better', 'Mayor es mejor (≥ meta)'),
            ('lower_is_better', 'Menor es mejor (≤ meta)'),
        ],
        string='Dirección de la Meta',
        default='higher_is_better',
        required=True,
        help='Define cómo se calcula si el KPI está en verde o rojo.',
    )

    current_value = fields.Float(
        string='Valor Esta Semana',
        tracking=True,
        help='Valor real registrado en la semana en curso.',
    )

    weekly_status = fields.Selection(
        selection=[
            ('green', 'En Meta ✅'),
            ('red', 'Fuera de Meta 🔴'),
            ('not_reported', 'Sin Reportar ⬜'),
        ],
        string='Estado Semanal',
        compute='_compute_weekly_status',
        store=True,
    )

    record_ids = fields.One2many(
        comodel_name='eos.kpi.record',
        inverse_name='kpi_id',
        string='Historial Semanal',
    )

    unit_of_measure = fields.Char(
        string='Unidad de Medida',
        help='Ej: "clientes", "%", "COP", "tickets".',
    )

    description = fields.Text(
        string='Descripción y Contexto',
        help='Cómo se mide este indicador y qué información fuente se usa.',
    )

    # ---------------------------------------------------------------
    # COMPUTE
    # ---------------------------------------------------------------
    @api.depends('current_value', 'goal_value', 'goal_direction')
    def _compute_weekly_status(self):
        for record in self:
            if record.current_value == 0.0 and record.goal_value != 0.0:
                record.weekly_status = 'not_reported'
            elif record.goal_direction == 'higher_is_better':
                record.weekly_status = 'green' if record.current_value >= record.goal_value else 'red'
            else:
                record.weekly_status = 'green' if record.current_value <= record.goal_value else 'red'

    def action_log_weekly_record(self):
        """
        Guarda el valor actual como registro histórico de esta semana
        y genera una entrada en el Chatter con el resultado.
        """
        self.ensure_one()
        today = fields.Date.today()
        # Calcular el número de semana ISO
        week_number = today.isocalendar()[1]
        year = today.year

        # Crear el registro histórico
        self.env['eos.kpi.record'].create({
            'kpi_id': self.id,
            'date': today,
            'week_number': week_number,
            'year': year,
            'value': self.current_value,
            'goal_value': self.goal_value,
            'status': self.weekly_status,
            'reported_by': self.env.user.id,
        })

        # Log en chatter
        status_label = '✅ EN META' if self.weekly_status == 'green' else '🔴 FUERA DE META'
        self.message_post(
            body=f'<b>Registro Semanal W{week_number}/{year}</b>: '
                 f'Valor = {self.current_value} {self.unit_of_measure or ""} | '
                 f'Meta = {self.goal_value} | {status_label}',
        )


class EosKpiRecord(models.Model):
    """
    REGISTRO SEMANAL DE KPI — Historial de valores por semana.

    Cada vez que se registra el valor semanal de un KPI, se crea
    un registro aquí para mantener el historial completo y permitir
    análisis de tendencias.

    En la BD: eos_kpi_record
    """

    _name = 'eos.kpi.record'
    _description = 'EOS - Registro Histórico de KPI'
    _order = 'year desc, week_number desc'

    kpi_id = fields.Many2one(
        comodel_name='eos.kpi',
        string='KPI',
        required=True,
        ondelete='cascade',
    )

    date = fields.Date(string='Fecha', required=True)
    week_number = fields.Integer(string='Semana')
    year = fields.Integer(string='Año')

    value = fields.Float(string='Valor Real', required=True)
    goal_value = fields.Float(string='Meta de la Semana')

    status = fields.Selection(
        selection=[
            ('green', 'En Meta ✅'),
            ('red', 'Fuera de Meta 🔴'),
        ],
        string='Estado',
        required=True,
    )

    reported_by = fields.Many2one(
        comodel_name='res.users',
        string='Reportado por',
        default=lambda self: self.env.user,
    )

    notes = fields.Char(string='Comentario', help='Breve explicación del valor de esta semana.')


class EosOkr(models.Model):
    """
    OKR — Objetivo y Resultados Clave.

    Los OKRs complementan las Rocas de EOS con una estructura más
    granular: un Objetivo inspira y orienta, mientras que los
    Resultados Clave son las métricas concretas que demuestran su logro.

    Vinculación con EOS:
    - Un OKR se alinea con una Roca (prioridad trimestral)
    - Los Resultados Clave son los indicadores medibles de esa Roca

    En la BD: eos_okr
    """

    _name = 'eos.okr'
    _description = 'EOS - OKR (Objetivo y Resultados Clave)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'company_id, date_end desc'

    name = fields.Char(
        string='Objetivo',
        required=True,
        tracking=True,
        help='El objetivo cualitativo e inspirador. Debe responder: '
             '"¿Qué queremos lograr?" Ej: "Establecer una operación de ventas escalable".',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )

    owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable del OKR',
        required=True,
        tracking=True,
    )

    rock_id = fields.Many2one(
        comodel_name='eos.vision.rock',
        string='Roca Asociada',
        tracking=True,
        help='Roca del V/TO a la que se alinea este OKR.',
    )

    date_start = fields.Date(string='Fecha de Inicio', tracking=True)
    date_end = fields.Date(string='Fecha de Fin', required=True, tracking=True)

    period = fields.Selection(
        selection=[
            ('q1', 'Q1'), ('q2', 'Q2'), ('q3', 'Q3'), ('q4', 'Q4'),
            ('annual', 'Anual'),
        ],
        string='Período',
        tracking=True,
    )

    week_number = fields.Char(
        string='Semana',
        default=lambda self: str(datetime.date.today().isocalendar()[1]),
        tracking=True,
    )

    year = fields.Char(
        string='Año',
        default=lambda self: str(datetime.date.today().year),
        tracking=True,
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('active', 'Activo'),
            ('completed', 'Completado'),
            ('cancelled', 'Cancelado'),
        ],
        string='Estado',
        default='draft',
        tracking=True,
        copy=False,
    )

    key_result_ids = fields.One2many(
        comodel_name='eos.okr.key.result',
        inverse_name='okr_id',
        string='Resultados Clave',
    )

    overall_progress = fields.Float(
        string='Progreso General (%)',
        compute='_compute_overall_progress',
        store=True,
        help='Promedio del progreso de todos los Resultados Clave.',
    )

    description = fields.Text(string='Descripción y Contexto')

    @api.depends('key_result_ids.progress')
    def _compute_overall_progress(self):
        for record in self:
            krs = record.key_result_ids
            if krs:
                record.overall_progress = sum(krs.mapped('progress')) / len(krs)
            else:
                record.overall_progress = 0.0

    def action_activate(self):
        for r in self:
            r.write({'state': 'active'})

    def action_complete(self):
        for r in self:
            r.write({'state': 'completed'})

    def action_rollover_next_week(self):
        """
        Cierra el listado actual y transfiere solo los RC que NO están completados 
        a un reporte de la semana siguiente.
        """
        for record in self:
            next_week = int(record.week_number) + 1
            next_year = int(record.year)
            if next_week > 52:
                next_week = 1
                next_year += 1

            new_okr = record.copy({
                'state': 'active',
                'week_number': str(next_week),
                'year': str(next_year),
                'key_result_ids': False,
            })

            for kr in record.key_result_ids.filtered(lambda x: x.status != 'completed'):
                kr.copy({
                    'okr_id': new_okr.id,
                })

            record.write({'state': 'completed'})
            
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class EosOkrKeyResult(models.Model):
    """
    RESULTADO CLAVE — Métrica individual de un OKR.

    Cada Resultado Clave es una métrica específica, medible y verificable
    que, al cumplirse, demuestra el logro del Objetivo.

    En la BD: eos_okr_key_result
    """

    _name = 'eos.okr.key.result'
    _description = 'EOS - Resultado Clave de OKR'
    _order = 'okr_id, sequence'

    sequence = fields.Integer(default=10)

    okr_id = fields.Many2one(
        comodel_name='eos.okr',
        string='OKR',
        required=True,
        ondelete='cascade',
    )

    name = fields.Char(
        string='Resultado Clave',
        required=True,
        help='Descripción medible. Ej: "Incrementar el MRR de 50M a 100M COP".',
    )

    owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        help='Persona responsable de este Resultado Clave específico.',
    )

    baseline_value = fields.Float(string='Valor Inicial (Línea Base)')
    target_value = fields.Float(string='Valor Objetivo', required=True)
    current_value = fields.Float(string='Valor Actual', tracking=True)

    unit = fields.Char(string='Unidad', help='Ej: "COP", "%", "clientes".')

    progress = fields.Float(
        string='Progreso (%)',
        compute='_compute_progress',
        store=True,
    )

    status = fields.Selection(
        selection=[
            ('on_track', 'En Camino ✅'),
            ('at_risk', 'En Riesgo ⚠️'),
            ('off_track', 'Fuera de Camino 🔴'),
            ('completed', 'Completado ✔'),
        ],
        string='Estado',
        compute='_compute_progress',
        store=True,
    )

    @api.depends('baseline_value', 'target_value', 'current_value')
    def _compute_progress(self):
        """
        Calcula el progreso como porcentaje de avance desde la línea base
        hasta el objetivo.
        """
        for record in self:
            delta_total = record.target_value - record.baseline_value
            if delta_total == 0:
                record.progress = 100.0
                record.status = 'completed'
            else:
                delta_current = record.current_value - record.baseline_value
                pct = (delta_current / delta_total) * 100
                record.progress = min(max(pct, 0.0), 100.0)

                if pct >= 100:
                    record.status = 'completed'
                elif pct >= 70:
                    record.status = 'on_track'
                elif pct >= 40:
                    record.status = 'at_risk'
                else:
                    record.status = 'off_track'
