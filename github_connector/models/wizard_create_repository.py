# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class WizardCreateRepository(models.TransientModel):
    _name = 'wizard.create.repository'
    _inherit = ['github.repository']

    # Overload Columns Section
    name = fields.Char(readonly=False)
    website = fields.Char(readonly=False)
    description = fields.Char(readonly=False)
    organization_id = fields.Many2one(readonly=False)

    @api.multi
    def get_github_data_from_odoo(self):
        self.ensure_one()
        res = super(WizardCreateRepository, self).get_github_data_from_odoo()
        return res

    @api.multi
    def button_create_in_github(self):
        self.ensure_one()
        new_item = self.create_in_github(self.env['github.repository'])
        return new_item.get_action()
