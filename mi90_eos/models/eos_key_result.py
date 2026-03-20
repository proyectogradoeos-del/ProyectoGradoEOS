from odoo import models, fields, api


class EosKeyResult(models.Model):
    _name = 'eos.key_result'
    _description = 'EOS Key Result'

    name = fields.Char(string='Key Result', required=True)
    rock_id = fields.Many2one('eos.rock', string='Rock', ondelete='cascade', index=True)
    target_value = fields.Float(string='Target', required=False, default=100.0)
    current_value = fields.Float(string='Current', default=0.0)
    unit = fields.Char(string='Unit')
    weight = fields.Float(string='Weight', default=1.0)
    kr_type = fields.Selection([
        ('baseline', 'Línea Base'),
        ('positive', 'Métrica Positiva (más es mejor)'),
        ('negative', 'Métrica Negativa (menos es mejor)'),
        ('threshold', 'Umbral (rango objetivo)'),
        ('milestone', 'Hito (no métrico)')
    ], string='Tipo KR', default='positive')
    status = fields.Selection([('new', 'New'), ('ontrack', 'On Track'), ('offtrack', 'Off Track'), ('done', 'Done')], default='new')
    last_update = fields.Datetime(string='Last Update')
    note = fields.Text(string='Note')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # trigger rock progress recompute
        records.mapped('rock_id')._compute_progress()
        return records

    def write(self, vals):
        res = super().write(vals)
        # recompute affected rocks
        self.mapped('rock_id')._compute_progress()
        return res
