# -*- coding: utf-8 -*-
"""
COMPONENTE 6 — TRACCIÓN (Traction)
=====================================
La Tracción es el resultado de tener los otros 5 componentes funcionando.
Es la disciplina y la rendición de cuentas que convierte la Visión en resultados.

Las dos herramientas principales son:

1. REUNIÓN L10 (Level 10 Meeting):
   La reunión semanal de 90 minutos del Leadership Team.
   Se llama "Level 10" porque el objetivo es que cada reunión sea
   calificada 10/10 por todos los participantes.

   AGENDA FIJA (no se cambia):
   - 5 min: Check-in (¿cómo está cada quien? — buenas noticias)
   - 5 min: Scorecard (revisión de KPIs — ¿verde o rojo?)
   - 5 min: Revisión de Rocas (¿on track o off track?)
   - 5 min: Titulares del cliente y del empleado
   - 5 min: Revisión de To-dos (¿completados o no?)
   - 60 min: IDS — Identificar, Discutir, Resolver (Issues)
   - 5 min: Cierre (evaluar la reunión / próxima agenda)

2. TO-DOS (Compromisos semanales):
   Lista de compromisos con dueño y fecha. Se revisan en cada L10.
   Un To-Do incompleto se convierte en issue a discutir.

Modelos:
  - EosMeeting: Reunión L10 completa
  - EosMeetingAttendee: Participante de la reunión
  - EosTodo: Compromiso individual de To-Do list

"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime


class EosMeeting(models.Model):
    """
    REUNIÓN L10 — Level 10 Meeting de EOS.

    La L10 es la reunión más importante de EOS. Su poder radica en
    la agenda FIJA y la disciplina de seguirla cada semana sin importar
    lo que pase. No es negociable cambiar la agenda.

    El nombre "Level 10" viene del objetivo: al final de cada reunión,
    los participantes la califican del 1 al 10. El objetivo es consistentemente
    llegar a 10/10.

    En la BD: eos_meeting
    """

    _name = 'eos.meeting'
    _description = 'EOS - Reunión L10 (Level 10 Meeting)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(
        string='Nombre de la Reunión',
        required=True,
        tracking=True,
        help='Ej: "L10 Semanal TLP Holding — Semana 20, 2025"',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )

    meeting_type = fields.Selection(
        selection=[
            ('l10_weekly', 'L10 Semanal (90 min)'),
            ('quarterly', 'Revisión Trimestral (1 día)'),
            ('annual', 'Planificación Anual (2 días)'),
            ('focus_day', 'Día de Enfoque (Extraordinaria)'),
        ],
        string='Tipo de Reunión',
        default='l10_weekly',
        required=True,
        tracking=True,
    )

    date = fields.Datetime(
        string='Fecha y Hora',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )

    duration_minutes = fields.Integer(
        string='Duración (minutos)',
        default=90,
        help='La L10 semanal dura exactamente 90 minutos.',
    )

    facilitator_id = fields.Many2one(
        comodel_name='res.users',
        string='Facilitador',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
        help='Quien modera y guía la agenda de la reunión.',
    )

    state = fields.Selection(
        selection=[
            ('scheduled', 'Programada 📅'),
            ('in_progress', 'En Curso 🔴'),
            ('completed', 'Completada ✅'),
            ('cancelled', 'Cancelada'),
        ],
        string='Estado',
        default='scheduled',
        required=True,
        tracking=True,
        copy=False,
    )

    # ---------------------------------------------------------------
    # Participantes
    # ---------------------------------------------------------------
    attendee_ids = fields.One2many(
        comodel_name='eos.meeting.attendee',
        inverse_name='meeting_id',
        string='Participantes',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 1: CHECK-IN (5 min)
    # ---------------------------------------------------------------
    checkin_notes = fields.Text(
        string='Check-In — Buenas Noticias (5 min)',
        help='Cada participante comparte brevemente una buena noticia '
             'personal o profesional. El objetivo es conectar al equipo '
             'y comenzar con energía positiva.',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 2: SCORECARD (5 min)
    # ---------------------------------------------------------------
    scorecard_id = fields.Many2one(
        comodel_name='eos.scorecard',
        string='Scorecard Revisado',
        tracking=True,
        help='Scorecard revisado en esta reunión.',
    )

    scorecard_notes = fields.Text(
        string='Notas del Scorecard (5 min)',
        help='Observaciones sobre los KPIs fuera de meta. '
             'Los KPIs en rojo se agregan como Issues a resolver.',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 3: REVISIÓN DE ROCAS (5 min)
    # ---------------------------------------------------------------
    rocks_review_notes = fields.Text(
        string='Revisión de Rocas (5 min)',
        help='Estado de cada Roca: "On Track" o "Off Track". '
             'Las Rocas fuera de camino se convierten en Issues.',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 4: TITULARES (5 min)
    # ---------------------------------------------------------------
    customer_headlines = fields.Text(
        string='Titulares del Cliente (5 min)',
        help='Noticias breves sobre clientes: nuevos contratos, '
             'cancelaciones, quejas o felicitaciones importantes.',
    )

    employee_headlines = fields.Text(
        string='Titulares del Empleado (5 min)',
        help='Noticias breves sobre el equipo: contrataciones, '
             'renuncias, reconocimientos o situaciones relevantes.',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 5: REVISIÓN DE TO-DOS (5 min)
    # ---------------------------------------------------------------
    todo_completion_rate = fields.Float(
        string='% To-Dos Completados',
        compute='_compute_todo_rate',
        store=True,
        help='Porcentaje de To-Dos de la semana anterior completados. '
             'EOS espera un mínimo del 80% de cumplimiento.',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 6: IDS — Issues (60 min)
    # ---------------------------------------------------------------
    issue_ids = fields.Many2many(
        comodel_name='eos.issue',
        string='Issues Discutidos (IDS)',
        help='Issues resueltos o discutidos en esta reunión.',
    )

    ids_notes = fields.Text(
        string='Notas del IDS (60 min)',
        help='Resumen de las decisiones tomadas durante el proceso IDS '
             'de la reunión.',
    )

    # ---------------------------------------------------------------
    # SECCIÓN 7: CIERRE (5 min)
    # ---------------------------------------------------------------
    next_meeting_date = fields.Datetime(
        string='Próxima Reunión',
        tracking=True,
    )

    rating_avg = fields.Float(
        string='Calificación Promedio de la Reunión',
        compute='_compute_rating_avg',
        store=True,
        help='Promedio de las calificaciones de los participantes (1-10). '
             'Una "Level 10 Meeting" debería tener un promedio de 10/10.',
    )

    closing_notes = fields.Text(
        string='Notas de Cierre',
        help='Compromisos finales, mensajes del equipo, notas generales.',
    )

    # ---------------------------------------------------------------
    # To-Dos generados en esta reunión
    # ---------------------------------------------------------------
    todo_ids = fields.One2many(
        comodel_name='eos.todo',
        inverse_name='meeting_id',
        string='To-Dos Creados en esta Reunión',
    )

    # ---------------------------------------------------------------
    # COMPUTES
    # ---------------------------------------------------------------
    @api.depends('attendee_ids.rating')
    def _compute_rating_avg(self):
        for record in self:
            rated = record.attendee_ids.filtered(lambda a: a.rating > 0)
            if rated:
                record.rating_avg = sum(rated.mapped('rating')) / len(rated)
            else:
                record.rating_avg = 0.0

    @api.depends('todo_ids.state')
    def _compute_todo_rate(self):
        for record in self:
            todos = record.todo_ids
            if todos:
                done = len(todos.filtered(lambda t: t.state == 'done'))
                record.todo_completion_rate = (done / len(todos)) * 100
            else:
                record.todo_completion_rate = 0.0

    # ---------------------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------------------
    def action_start_meeting(self):
        for record in self:
            record.write({'state': 'in_progress'})

    def action_complete_meeting(self):
        for record in self:
            record.write({'state': 'completed'})

    def action_cancel_meeting(self):
        for record in self:
            record.write({'state': 'cancelled'})


class EosMeetingAttendee(models.Model):
    """
    PARTICIPANTE DE REUNIÓN — Asistente a una L10 Meeting.

    Registra la asistencia y la calificación individual de cada
    participante al final de la reunión.

    En la BD: eos_meeting_attendee
    """

    _name = 'eos.meeting.attendee'
    _description = 'EOS - Participante de Reunión L10'
    _order = 'meeting_id, user_id'

    meeting_id = fields.Many2one(
        comodel_name='eos.meeting',
        string='Reunión',
        required=True,
        ondelete='cascade',
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Participante',
        required=True,
    )

    attended = fields.Boolean(
        string='Asistió',
        default=True,
    )

    rating = fields.Integer(
        string='Calificación de la Reunión (1-10)',
        default=0,
        help='¿Qué tan productiva fue esta reunión? 1 = muy mala, 10 = perfecta.',
    )

    @api.constrains('rating')
    def _check_rating(self):
        for record in self:
            if not (0 <= record.rating <= 10):
                raise ValidationError('La calificación debe estar entre 1 y 10.')


class EosTodo(models.Model):
    """
    TO-DO — Compromiso semanal del componente TRACCIÓN.

    Un To-Do es un compromiso concreto que debe completarse en 7 días.
    Tiene exactamente un dueño y se revisa en cada L10 Meeting.

    Diferencia entre Roca y To-Do:
    - ROCA: Proyecto estratégico de 90 días (trimestre)
    - TO-DO: Tarea táctica de 7 días (semana)

    Un To-Do no completado en la semana se convierte en Issue a discutir.

    En la BD: eos_todo
    """

    _name = 'eos.todo'
    _description = 'EOS - To-Do (Compromiso Semanal)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_due, owner_id'

    name = fields.Char(
        string='Compromiso',
        required=True,
        tracking=True,
        help='Descripción clara y accionable del compromiso. '
             'Debe ser completable en 7 días. '
             'Ej: "Enviar propuesta comercial a cliente X".',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
    )

    owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Dueño',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        help='Persona responsable de completar este To-Do.',
    )

    meeting_id = fields.Many2one(
        comodel_name='eos.meeting',
        string='Reunión en que se creó',
        tracking=True,
        help='L10 Meeting en la que se generó este compromiso.',
    )

    date_created = fields.Date(
        string='Fecha de Creación',
        default=fields.Date.today,
        readonly=True,
    )

    date_due = fields.Date(
        string='Fecha Límite',
        required=True,
        tracking=True,
        help='Un To-Do EOS se completa en 7 días (antes de la próxima L10).',
    )

    state = fields.Selection(
        selection=[
            ('pending', 'Pendiente'),
            ('done', 'Completado ✅'),
            ('not_done', 'No Completado ❌ → Issue'),
        ],
        string='Estado',
        default='pending',
        required=True,
        tracking=True,
        copy=False,
    )

    related_rock_id = fields.Many2one(
        comodel_name='eos.vision.rock',
        string='Roca Relacionada',
        help='Si este To-Do es un paso hacia el cumplimiento de una Roca.',
    )

    related_issue_id = fields.Many2one(
        comodel_name='eos.issue',
        string='Issue Relacionado',
        help='Si este To-Do es una tarea resultante de resolver un Issue.',
    )

    notes = fields.Text(string='Notas')

    # ---------------------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------------------
    def action_mark_done(self):
        for record in self:
            record.write({'state': 'done'})

    def action_mark_not_done(self):
        """
        Marca el To-Do como No Completado y sugiere crear un Issue.
        En EOS, un To-Do no completado debe convertirse en Issue.
        """
        for record in self:
            record.write({'state': 'not_done'})

    def action_create_issue_from_todo(self):
        """
        Genera automáticamente un Issue a partir de este To-Do no completado.
        Esto implementa el ciclo EOS: To-Do → Issue → IDS → Solución.
        """
        self.ensure_one()
        issue = self.env['eos.issue'].create({
            'name': f'[To-Do No Completado] {self.name}',
            'company_id': self.company_id.id,
            'identified_by': self.env.user.id,
            'issue_type': 'short_term',
            'root_cause': f'To-Do "{self.name}" asignado a '
                          f'{self.owner_id.name} no fue completado '
                          f'antes del {self.date_due}.',
        })
        self.write({'related_issue_id': issue.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Issue Creado',
            'res_model': 'eos.issue',
            'res_id': issue.id,
            'view_mode': 'form',
        }
