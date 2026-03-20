# -*- coding: utf-8 -*-

import logging
from odoo import models, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class Mi90EOSCompatPatches(models.AbstractModel):
    """Small compatibility patches executed after registry is ready.

    Goal: prevent Settings crash caused by legacy views that reference
    fields dropped in Odoo 17 (e.g., res.config.settings.stock_move_sms_validation).
    We disable such views defensively to restore Settings usability.
    """

    _name = 'mi90_eos.compat_patches'
    _description = 'Mi90 EOS Compatibility Patches'

    def _register_hook(self):
        # Run in superuser env, avoid access issues
        env = api.Environment(self.env.cr, SUPERUSER_ID, {})
        try:
            # Find any Settings views that reference the dropped field
            domain = [
                ('model', '=', 'res.config.settings'),
                ('arch_db', 'ilike', 'stock_move_sms_validation'),
            ]
            views = env['ir.ui.view'].with_context(active_test=False).search(domain)
            if views:
                # Only disable active ones; keep record but inactive
                actives = views.filtered(lambda v: v.active)
                if actives:
                    actives.write({'active': False})
                    _logger.warning(
                        "mi90_eos: Disabled %s legacy Settings view(s) referencing 'stock_move_sms_validation' to prevent crash.",
                        len(actives),
                    )
        except Exception as e:
            _logger.exception("mi90_eos: Failed applying compatibility patch for Settings views: %s", e)
