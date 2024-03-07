# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WizardLoadGithubModel(models.TransientModel):
    _name = "wizard.load.github.model"
    _description = "Wizard Load Github Model"

    # Columns Section
    github_type = fields.Selection(
        selection=[
            ("organization", "Organization"),
            ("repository", "Repository"),
            ("user", "User"),
        ],
        string="Github Type Name",
        default="organization",
        required=True,
    )

    name = fields.Char(string="Github Name", required=True)

    child_update = fields.Boolean(string="Update Child Objects", default=False)

    def button_create_from_github(self):
        for wizard in self:
            if wizard.github_type == "organization":
                github_model = self.env["github.organization"]
            elif wizard.github_type == "user":
                github_model = self.env["res.partner"]
            elif wizard.github_type == "repository":
                github_model = self.env["github.repository"]
            my_obj = github_model.create_from_name(wizard.name)
            if wizard.child_update:
                my_obj.update_from_github(True)
