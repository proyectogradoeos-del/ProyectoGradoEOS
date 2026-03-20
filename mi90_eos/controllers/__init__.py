# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class EOSController(http.Controller):

    @http.route('/eos/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kwargs):
        """Dashboard principal EOS"""
        return request.render('mi90_eos.dashboard_template')

    @http.route('/eos/scorecard', type='http', auth='user', website=True)
    def scorecard(self, **kwargs):
        """Scorecard EOS"""
        return request.render('mi90_eos.scorecard_template')

    @http.route('/eos/rocks', type='http', auth='user', website=True)
    def rocks(self, **kwargs):
        """Rocas EOS"""
        return request.render('mi90_eos.rocks_template')

    @http.route('/eos/todos', type='http', auth='user', website=True)
    def todos(self, **kwargs):
        """To-Dos EOS"""
        return request.render('mi90_eos.todos_template')

    @http.route('/eos/issues', type='http', auth='user', website=True)
    def issues(self, **kwargs):
        """Problemas EOS"""
        return request.render('mi90_eos.issues_template')

    @http.route('/eos/meetings', type='http', auth='user', website=True)
    def meetings(self, **kwargs):
        """Reuniones EOS"""
        return request.render('mi90_eos.meetings_template')

    @http.route('/eos/headlines', type='http', auth='user', website=True)
    def headlines(self, **kwargs):
        """Titulares EOS"""
        return request.render('mi90_eos.headlines_template')

    @http.route('/eos/vto', type='http', auth='user', website=True)
    def vto(self, **kwargs):
        """V/TO® EOS"""
        return request.render('mi90_eos.vto_template')

    @http.route('/eos/accountability', type='http', auth='user', website=True)
    def accountability(self, **kwargs):
        """Organigrama de Responsabilidades EOS"""
        return request.render('mi90_eos.accountability_template')

    @http.route('/eos/oneonone', type='http', auth='user', website=True)
    def oneonone(self, **kwargs):
        """1-a-1 EOS"""
        return request.render('mi90_eos.oneonone_template')

    @http.route('/eos/process', type='http', auth='user', website=True)
    def process(self, **kwargs):
        """Proceso EOS"""
        return request.render('mi90_eos.process_template')

    @http.route('/eos/directory', type='http', auth='user', website=True)
    def directory(self, **kwargs):
        """Directorio EOS"""
        return request.render('mi90_eos.directory_template')

    @http.route('/eos/toolbox', type='http', auth='user', website=True)
    def toolbox(self, **kwargs):
        """EOS Toolbox™"""
        return request.render('mi90_eos.toolbox_template')
