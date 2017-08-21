# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval


class WizardUpdateFromGithub(models.TransientModel):
    _name = 'wizard.update.from.github'

    # Columns Section
    child_update = fields.Boolean(string='Update Child Objects', default=False)

    @api.multi
    def button_update_from_github(self):
        partial_commit = safe_eval(
            self.env['ir.config_parameter'].get_param(
                'git.partial_commit_during_analysis'))
        for wizard in self:
            model_obj = self.env[self._context['active_model']]
            for item in model_obj.browse(self._context['active_ids']):
                item.update_from_github(wizard.child_update)
                if partial_commit:
                    self._cr.commit()  # pylint: disable=invalid-commit
