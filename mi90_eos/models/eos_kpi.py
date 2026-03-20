from odoo import models, fields, api


class EosKPI(models.Model):
    _name = 'eos.kpi'
    _description = 'EOS KPI (Scorecard)'

    name = fields.Char(string='Metric', required=True)
    unit = fields.Char(string='Unit')
    target = fields.Float(string='Target')
    owner_id = fields.Many2one('res.users', string='Owner')
    value_ids = fields.One2many('eos.kpi.value', 'kpi_id', string='Values')


class EosKPIValue(models.Model):
    _name = 'eos.kpi.value'
    _description = 'EOS KPI Value'

    kpi_id = fields.Many2one('eos.kpi', string='KPI', ondelete='cascade', index=True)
    date = fields.Date(string='Date')
    value = fields.Float(string='Value')