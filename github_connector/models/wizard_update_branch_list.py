# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class WizardUpdateBranchList(models.TransientModel):
    _name = 'wizard.update.branch.list'

    @api.multi
    def button_update_branch_list(self):
        for wizard in self:
            repository_obj = self.env['github.repository']
            items = repository_obj.browse(self._context['active_ids'])
            items.button_sync_branch()
