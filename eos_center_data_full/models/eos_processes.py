# -*- coding: utf-8 -*-
"""
COMPONENTE 5 — PROCESOS (Processes)
=====================================
En EOS, el componente "Procesos" se basa en identificar los procesos
CRÍTICOS de la empresa (generalmente 6-10), documentarlos y asegurarse
de que TODOS los ejecuten de la MISMA MANERA.

Frase clave de EOS:
  "Documenta lo suficiente para que alguien con las habilidades
   correctas pueda ejecutarlo consistentemente."

EOS NO busca documentar todos los procesos ni crear manuales de 200 páginas.
Busca identificar los procesos que más impactan en los resultados y
estandarizarlos para que sean escalables y repetibles.

LOS 6-10 PROCESOS CLAVE TÍPICOS EN EOS:
  1. Marketing / Generación de demanda
  2. Ventas / Conversión
  3. Entrega del producto/servicio (Fulfillment)
  4. Experiencia del cliente (Customer Service)
  5. Contratación y Onboarding de empleados
  6. Contabilidad / Flujo de caja

Herramientas EOS usadas:
  - Process Documenter: Captura y versión del proceso
  - Seguimiento de adherencia: ¿Se está siguiendo el proceso?

Modelos:
  - EosProcess: Proceso crítico de la empresa
  - EosProcessStep: Paso individual dentro de un proceso
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EosProcess(models.Model):
    """
    PROCESO — Proceso crítico de la empresa documentado en EOS.

    Un proceso EOS se documenta en el formato "Paso a Paso":
    - Nombre claro
    - Dueño (quien es responsable de que se siga)
    - Pasos numerados con el responsable de cada uno
    - Criterios de calidad / Resultado esperado

    El objetivo es que el proceso sea lo suficientemente claro
    para que cualquier persona con las habilidades necesarias
    pueda ejecutarlo de la misma manera.

    En la BD: eos_process
    """

    _name = 'eos.process'
    _description = 'EOS - Proceso Crítico'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    sequence = fields.Integer(default=10)

    name = fields.Char(
        string='Nombre del Proceso',
        required=True,
        tracking=True,
        help='Nombre claro y descriptivo. Ej: "Proceso de Incorporación '
             'de Nuevos Clientes", "Proceso de Cierre de Ventas".',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )

    process_owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Dueño del Proceso',
        required=True,
        tracking=True,
        help='Responsable de que este proceso esté documentado, '
             'actualizado y se ejecute correctamente.',
    )

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Área Responsable',
        tracking=True,
    )

    process_category = fields.Selection(
        selection=[
            ('marketing', 'Marketing / Generación de Demanda'),
            ('sales', 'Ventas / Conversión'),
            ('fulfillment', 'Entrega del Producto/Servicio'),
            ('customer_service', 'Experiencia del Cliente'),
            ('hr', 'Recursos Humanos / Onboarding'),
            ('finance', 'Finanzas / Contabilidad'),
            ('operations', 'Operaciones Generales'),
            ('other', 'Otro'),
        ],
        string='Categoría',
        default='operations',
        required=True,
        tracking=True,
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('documented', 'Documentado'),
            ('followed', 'Seguido por Todos ✅'),
            ('needs_update', 'Requiere Actualización ⚠️'),
        ],
        string='Estado del Proceso',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
        help='Los procesos EOS tienen 4 fases:\n'
             '1. Borrador: en construcción\n'
             '2. Documentado: escrito y aprobado\n'
             '3. Seguido: el equipo lo ejecuta consistentemente\n'
             '4. Necesita actualización: cambios requeridos',
    )

    # ---------------------------------------------------------------
    # Documentación del proceso
    # ---------------------------------------------------------------
    purpose = fields.Text(
        string='Propósito del Proceso',
        tracking=True,
        help='¿Por qué existe este proceso? ¿Qué problema resuelve? '
             '¿Cuál es el resultado esperado al ejecutarlo correctamente?',
    )

    scope = fields.Text(
        string='Alcance (Inicio y Fin)',
        help='¿Cuándo empieza este proceso? ¿Cuándo termina? '
             '¿Qué está incluido y qué no?',
    )

    expected_output = fields.Text(
        string='Resultado Esperado',
        tracking=True,
        help='¿Cómo se ve el proceso completado exitosamente? '
             '¿Cuáles son los criterios de calidad?',
    )

    version = fields.Char(
        string='Versión',
        default='1.0',
        tracking=True,
        help='Control de versiones del proceso. Incrementar cuando '
             'se hacen cambios significativos.',
    )

    last_review_date = fields.Date(
        string='Última Revisión',
        tracking=True,
        help='Fecha de la última revisión formal del proceso.',
    )

    # ---------------------------------------------------------------
    # Pasos del proceso
    # ---------------------------------------------------------------
    step_ids = fields.One2many(
        comodel_name='eos.process.step',
        inverse_name='process_id',
        string='Pasos del Proceso',
    )

    step_count = fields.Integer(
        string='# Pasos',
        compute='_compute_step_count',
        store=True,
    )

    # ---------------------------------------------------------------
    # Métricas de adherencia
    # ---------------------------------------------------------------
    adherence_notes = fields.Text(
        string='Notas de Adherencia',
        help='¿El equipo está siguiendo este proceso? ¿Qué desviaciones '
             'se han observado? ¿Qué obstáculos impiden seguirlo?',
    )

    @api.depends('step_ids')
    def _compute_step_count(self):
        for record in self:
            record.step_count = len(record.step_ids)

    def action_view_steps(self):
        self.ensure_one()
        return {
            'name': 'Pasos',
            'type': 'ir.actions.act_window',
            'res_model': 'eos.process.step',
            'view_mode': 'list,form',
            'domain': [('process_id', '=', self.id)],
            'context': {'default_process_id': self.id},
        }


    def action_mark_documented(self):
        for record in self:
            record.write({'state': 'documented'})

    def action_mark_followed(self):
        for record in self:
            record.write({'state': 'followed'})

    def action_needs_update(self):
        for record in self:
            record.write({'state': 'needs_update'})


class EosProcessStep(models.Model):
    """
    PASO DEL PROCESO — Instrucción individual dentro de un proceso EOS.

    Cada paso tiene:
    - Número de secuencia
    - Descripción clara de la acción a realizar
    - Responsable de ese paso específico
    - Herramientas o sistemas que se usan

    EOS recomienda que los pasos sean lo suficientemente específicos
    para garantizar consistencia, pero no tan detallados que se
    vuelvan una burocracia imposible de seguir.

    En la BD: eos_process_step
    """

    _name = 'eos.process.step'
    _description = 'EOS - Paso de Proceso'
    _order = 'process_id, sequence'

    sequence = fields.Integer(
        string='Paso #',
        required=True,
        default=10,
        help='Número de orden del paso (ej. 10, 20, 30 para dejar espacio '
             'entre pasos y poder insertar nuevos sin reordenar).',
    )

    process_id = fields.Many2one(
        comodel_name='eos.process',
        string='Proceso',
        required=True,
        ondelete='cascade',
    )

    name = fields.Char(
        string='Descripción del Paso',
        required=True,
        help='Instrucción clara y accionable. '
             'Ej: "Enviar correo de bienvenida con credenciales de acceso".',
    )

    step_owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable del Paso',
        help='Rol o persona que ejecuta este paso específico.',
    )

    tools_used = fields.Char(
        string='Herramientas / Sistemas',
        help='Software, formularios o recursos necesarios para este paso. '
             'Ej: "Odoo CRM", "Google Drive", "Contrato PDF".',
    )

    expected_time = fields.Float(
        string='Tiempo Estimado (horas)',
        help='Tiempo promedio que toma completar este paso.',
    )

    is_critical = fields.Boolean(
        string='¿Paso Crítico?',
        help='Marcar si este paso es especialmente importante '
             'para la calidad o el éxito del proceso completo.',
    )

    notes = fields.Text(
        string='Notas Adicionales',
        help='Aclaraciones, excepciones o consejos para ejecutar '
             'este paso correctamente.',
    )

    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string='Documentos de Referencia',
        help='Plantillas, formularios o guías relacionadas con este paso.',
    )
