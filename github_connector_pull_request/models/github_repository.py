#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class GithubRepository(models.Model):
    _inherit = "github.repository"

    pull_request_ids = fields.One2many(
        comodel_name="github.pull_request",
        inverse_name="repository_id",
        string="Pull Requests",
    )
    pull_request_qty = fields.Integer(
        string="Pull Request Quantity",
        compute="_compute_pull_request_qty",
        store=True,
    )

    @api.depends("pull_request_ids.repository_id")
    def _compute_pull_request_qty(self):
        for repository in self:
            repository.pull_request_qty = len(repository.pull_request_ids)

    def action_github_pull_requests(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector_pull_request.github_pull_request_action"
        )
        action["context"] = dict(self.env.context)
        action["context"]["search_default_repository_id"] = self.id
        return action

    def button_sync_pull_request(self):
        for repository in self.filtered(lambda r: not r.is_ignored):
            gh_repo = repository.find_related_github_object()
            gh_prs = gh_repo.get_pulls()
            for gh_pr in gh_prs:
                pull_request = (
                    self.env["github.pull_request"]
                    .with_context(
                        repository_id=repository.id,
                    )
                    .get_from_id_or_create(
                        gh_data=gh_pr,
                    )
                )
                pull_request.update_from_github(False)

    @api.model
    def cron_sync_pull_request(self):
        repositories = self.search([])
        repositories.button_sync_pull_request()
