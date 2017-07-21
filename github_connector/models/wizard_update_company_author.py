# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class WizardUpdateCompanyAuthor(models.TransientModel):
    _name = 'wizard.update.company.author'

    # Columns Section
    corporate_partner_id = fields.Many2one(
        string='Company', comodel_name='res.partner',
        domain="[('is_company', '=', True)]")

    @api.multi
    def button_update_company_author(self):
        for wizard in self:
            model_obj = self.env[self._context['active_model']]
            items = model_obj.browse(self._context['active_ids'])
            items.company_author_id = wizard.corporate_partner_id
