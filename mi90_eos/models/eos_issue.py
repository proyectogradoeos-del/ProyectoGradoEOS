from odoo import models, fields, api


class EosIssue(models.Model):
    _name = 'eos.issue'
    _description = 'EOS Issue'

    name = fields.Char(string='Title', required=True, index=True)
    description = fields.Text(string='Description')
    priority = fields.Selection([('low','Low'),('medium','Medium'),('high','High')], default='medium')
    resolved = fields.Boolean(string='Resolved', default=False)
    owner_id = fields.Many2one('res.users', string='Owner', ondelete='set null')
    created_at = fields.Datetime(string='Created At', readonly=True, default=fields.Datetime.now)
    updated_at = fields.Datetime(string='Updated At', readonly=True)

    def write(self, vals):
        res = super().write(vals)
        for r in self:
            r.updated_at = fields.Datetime.now()
        return res

    def action_create_todo(self):
        """Create a To-Do from this Issue and open it.
        - Prefills name/description/owner.
        - Links meeting if invoked from a meeting context.
        """
        self.ensure_one()
        ctx = dict(self.env.context or {})
        meeting_id = False
        if ctx.get('active_model') == 'eos.meeting' and ctx.get('active_id'):
            meeting_id = ctx.get('active_id')
        elif ctx.get('default_meeting_id'):
            meeting_id = ctx.get('default_meeting_id')

        todo_vals = {
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id.id if self.owner_id else False,
            'status': 'todo',
            'meeting_id': meeting_id or False,
            'issue_id': self.id,
        }
        todo = self.env['eos.todo'].create(todo_vals)

        action = self.env.ref('mi90_eos.action_eos_todo').read()[0]
        action.update({
            'res_id': todo.id,
            'views': [(False, 'form')],
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_meeting_id': meeting_id} if meeting_id else {},
        })
        return action
