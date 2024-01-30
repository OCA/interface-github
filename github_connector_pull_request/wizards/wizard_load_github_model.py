#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WizardLoadGithubModel(models.TransientModel):
    _inherit = "wizard.load.github.model"

    github_type = fields.Selection(
        selection_add=[("pr", "Pull Request URL")],
        ondelete={"pr": "cascade"},
    )

    def button_create_from_github(self):
        pull_request_model = self.env["github.pull_request"]
        pull_request_wizards = self.filtered(lambda w: w.github_type == "pr")
        for wizard in pull_request_wizards:
            pr_url = wizard.name
            pull_request_model.create_from_name(
                pr_url,
            )

        return super(
            WizardLoadGithubModel, self - pull_request_wizards
        ).button_create_from_github()
