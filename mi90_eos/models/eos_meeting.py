from odoo import models, fields, api
from datetime import timedelta


class EosMeeting(models.Model):
    _name = 'eos.meeting'
    _description = 'EOS Meeting (L10)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Title', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    start_datetime = fields.Datetime(string='Start Date/Time', help='Fecha y hora de inicio de la L10 (para recordatorios)')
    attendees = fields.Many2many('res.users', string='Attendees')
    notes = fields.Text(string='Notes')
    decisions = fields.Text(string='Decisions')
    agenda_notes = fields.Text(string='Agenda/Notas')
    created_at = fields.Datetime(string='Created At', readonly=True, default=fields.Datetime.now)
    # Roles sugeridos en L10
    integrator_id = fields.Many2one('res.users', string='Integrador')
    time_keeper_id = fields.Many2one('res.users', string='Time Keeper')
    # Responsable de convertir Issues en To-Dos y gestionar la cascada
    issues_to_todos_id = fields.Many2one('res.users', string='Resp. Issues→To-Dos/Cascada')
    # Lista de chequeo previa a la reunión
    precheck_scorecard = fields.Boolean(string='Scorecard actualizado')
    precheck_rocks = fields.Boolean(string='Rocas actualizadas')
    precheck_todos = fields.Boolean(string='To-Dos revisados')
    # Puntuación de la reunión (0-10)
    score = fields.Integer(string='Puntuación (0-10)', default=10)
    todo_ids = fields.One2many('eos.todo', 'meeting_id', string='To-Dos')
    todo_count = fields.Integer(string='To-Dos', compute='_compute_todo_count')
    reminder_1h_sent = fields.Boolean(string='1h Reminder Sent', default=False, readonly=True)
    reminder_5m_sent = fields.Boolean(string='5m Reminder Sent', default=False, readonly=True)

    def _compute_todo_count(self):
        for rec in self:
            rec.todo_count = len(rec.todo_ids)

    def action_view_todos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'To-Do',
            'res_model': 'eos.todo',
            'view_mode': 'kanban,tree,form',
            'domain': [('meeting_id', '=', self.id)],
            'context': {
                'default_meeting_id': self.id,
                'search_default_pending': 1,
            },
            'target': 'current',
        }

    @api.constrains('score')
    def _check_score_range(self):
        for rec in self:
            if rec.score is not None and (rec.score < 0 or rec.score > 10):
                rec.score = max(0, min(10, rec.score))

    def _get_user_partners(self, users):
        partners = users.mapped('partner_id').filtered(lambda p: p and p.active)
        return partners.ids

    def _send_message(self, body_html, partner_ids):
        for rec in self:
            if not partner_ids:
                continue
            rec.message_post(body=body_html, subtype_xmlid='mail.mt_comment', partner_ids=partner_ids)

    def cron_send_pre_meeting_reminders(self):
        """Cron job to send reminders 60 and 5 minutes prior to meeting start_datetime.
        - 60 min: remind Integrator/TimeKeeper about precheck items pending.
        - 5  min: remind attendees to ensure focus/logistics.
        """
        now = fields.Datetime.now()
        upcoming = self.search([('start_datetime', '!=', False),
                                ('start_datetime', '>=', now - timedelta(minutes=2)),
                                ('start_datetime', '<=', now + timedelta(minutes=70))])
        for rec in upcoming:
            start = rec.start_datetime
            if not start:
                continue
            delta = start - now
            minutes = int(delta.total_seconds() // 60)

            # 60-minute reminder window (59..61) and not sent yet
            if 59 <= minutes <= 61 and not rec.reminder_1h_sent:
                pending = []
                if not rec.precheck_scorecard:
                    pending.append('Scorecard actualizado')
                if not rec.precheck_rocks:
                    pending.append('Rocas actualizadas')
                if not rec.precheck_todos:
                    pending.append('To-Dos revisados')
                if pending:
                    targets = (rec.integrator_id | rec.time_keeper_id).sudo()
                    partners = self._get_user_partners(targets)
                    body = (
                        f"<p>Recordatorio L10 en 60 minutos: <b>{rec.name}</b></p>"
                        f"<p>Elementos pendientes de preparación:</p>"
                        f"<ul>{''.join(f'<li>{p}</li>' for p in pending)}</ul>"
                        f"<p>Fecha/Hora: {fields.Datetime.to_string(start)}</p>"
                    )
                    rec._send_message(body, partners)
                rec.reminder_1h_sent = True

            # 5-minute reminder window (4..6) and not sent yet
            if 4 <= minutes <= 6 and not rec.reminder_5m_sent:
                targets = (rec.attendees | rec.integrator_id | rec.time_keeper_id).sudo()
                partners = self._get_user_partners(targets)
                body = (
                    f"<p>Recordatorio L10 en 5 minutos: <b>{rec.name}</b></p>"
                    f"<p>Por favor: silenciar WIFL/teléfono/ruido y conectarse puntualmente.</p>"
                    f"<p>Fecha/Hora: {fields.Datetime.to_string(start)}</p>"
                )
                rec._send_message(body, partners)
                rec.reminder_5m_sent = True
