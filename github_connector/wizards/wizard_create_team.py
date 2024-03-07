# Copyright (C) 2017-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WizardCreateTeam(models.TransientModel):
    _name = "wizard.create.team"
    _description = "Wizard Create Team"
    _inherit = ["github.team"]

    # Overload Columns Section
    name = fields.Char(readonly=False)
    description = fields.Char(readonly=False)
    organization_id = fields.Many2one(readonly=False)
    privacy = fields.Selection(readonly=False)

    # Columns Section
    wizard_partner_ids = fields.Many2many(
        string="Team Members",
        comodel_name="res.partner",
        domain="[('github_name', '!=', False)]",
    )

    wizard_repository_ids = fields.Many2many(
        string="Team Repositories", comodel_name="github.repository"
    )

    def get_github_data_from_odoo(self):
        self.ensure_one()
        res = super().get_github_data_from_odoo()
        res.update(
            {
                "maintainers": [
                    x.github_name for x in self.wizard_partner_ids if x.github_name
                ],
                "repo_names": [
                    x.github_name for x in self.wizard_repository_ids if x.github_name
                ],
            }
        )
        return res

    def button_create_in_github(self):
        self.ensure_one()
        new_item = self.env["github.team"].create_in_github()
        return new_item.get_action()
