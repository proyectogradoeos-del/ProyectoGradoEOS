from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EosTodo(models.Model):
    _name = 'eos.todo'
    _description = 'EOS To-Do'
    _order = 'date_create desc'

    name = fields.Char(string='Title', required=True, index=True)
    description = fields.Text(string='Description')
    owner_id = fields.Many2one('res.users', string='Owner', ondelete='set null', index=True, default=lambda self: self.env.user)
    due_date = fields.Date(string='Due Date', index=True)
    status = fields.Selection([
        ('todo', 'Por Hacer'),
        ('in_progress', 'En Curso'),
        ('in_review', 'En Revisión'),
        ('done', 'Finalizado'),
        ('cancel', 'Cancelado')
    ], string='Status', default='todo', index=True)
    progress = fields.Float(string='Progress', compute='_compute_progress', store=True, group_operator='avg')
    rock_id = fields.Many2one('eos.rock', string='Related Rock', ondelete='set null')
    meeting_id = fields.Many2one('eos.meeting', string='L10 Meeting', ondelete='set null', index=True)
    issue_id = fields.Many2one('eos.issue', string='Issue', ondelete='set null', index=True)

    date_create = fields.Datetime(string='Created At', readonly=True, default=fields.Datetime.now)
    date_update = fields.Datetime(string='Updated At', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._compute_progress()
        return records

    def write(self, vals):
        vals['date_update'] = fields.Datetime.now()
        res = super().write(vals)
        # Recompute progress when status or other fields change
        if any(k in vals for k in ('name', 'description', 'status', 'owner_id', 'due_date')):
            for record in self:
                record._compute_progress()
        return res

    @api.depends('status')
    def _compute_progress(self):
        for todo in self:
            if todo.status == 'done':
                todo.progress = 100.0
            elif todo.status == 'in_review':
                todo.progress = 75.0
            elif todo.status == 'in_progress':
                todo.progress = 40.0
            elif todo.status == 'cancel':
                todo.progress = 0.0
            else:
                todo.progress = 0.0

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("El nombre de la tarea no puede estar vacío.")

    @api.constrains('due_date')
    def _check_due_date(self):
        for record in self:
            if record.due_date and record.due_date < fields.Date.today():
                # Only warn, don't block - tasks can have past due dates
                pass

    def action_start_progress(self):
        """Action to start working on the task"""
        self.write({'status': 'in_progress'})
        return True

    def action_mark_for_review(self):
        """Action to mark task for review"""
        self.write({'status': 'in_review'})
        return True

    def action_mark_done(self):
        """Action to mark task as done"""
        self.write({'status': 'done'})
        return True

    def action_reset_to_todo(self):
        """Action to reset task to todo"""
        self.write({'status': 'todo'})
        return True

    _sql_constraints = [
        ('name_not_empty', 'CHECK (char_length(name) > 0)', 'Task name must not be empty')
    ]
