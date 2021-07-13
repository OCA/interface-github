# Copyright (C) 2017-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WizardCreateRepository(models.TransientModel):
    _name = "wizard.create.repository"
    _description = "Wizard Create Repository"
    _inherit = ["github.repository"]

    # Overload Columns Section
    name = fields.Char(readonly=False)
    website = fields.Char(readonly=False)
    description = fields.Char(readonly=False)
    organization_id = fields.Many2one(readonly=False)

    def get_github_data_from_odoo(self):
        self.ensure_one()
        res = super().get_github_data_from_odoo()
        return res

    def button_create_in_github(self):
        self.ensure_one()
        new_item = self.create_in_github()
        return new_item.get_action()
