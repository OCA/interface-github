# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from collections import defaultdict

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class GithubRepository(models.Model):
    _inherit = "github.repository"

    runbot_id_external = fields.Integer(
        string="ID For Runbot",
        readonly=True,
        store=True,
        compute="_compute_runbot_id_external",
    )

    # Compute Section
    @api.depends("organization_id.runbot_parse_url")
    def _compute_runbot_id_external(self):
        url_done = defaultdict(list)
        for repository in self:
            url_done[repository.organization_id].append(repository)

        for organization_id, repositories in url_done.items():
            if organization_id.runbot_parse_url:
                req = requests.get(organization_id.runbot_parse_url, timeout=10)
                runbot_list = req.content.decode().split("\n")
                for item in runbot_list:
                    for repository in repositories:
                        if item.endswith(repository.complete_name):
                            repository.runbot_id_external = item.split("|")[0]

    def _fetch_all_branches(self):
        """Fetch all repo branches"""
        if self.organization_id.create_series is False:
            # sync without creating a series
            branch_obj = self.env["github.repository.branch"]
            for repository in self.filtered(lambda r: not r.is_ignored):
                gh_repo = repository.find_related_github_object()
                branch_ids = []
                for gh_branch in gh_repo.get_branches():
                    branch = branch_obj.create_or_update_from_name(
                        repository.id, gh_branch.name
                    )
                    branch_ids.append(branch.id)
                repository.repository_branch_ids = [(6, 0, branch_ids)]
        else:
            # sync with the creation of a series
            branch_obj = self.env["github.repository.branch"]
            for repository in self.filtered(lambda r: not r.is_ignored):
                gh_repo = repository.find_related_github_object()
                branch_ids = []
                correct_series = (
                    repository.organization_id.organization_serie_ids.mapped("name")
                )
                for gh_branch in gh_repo.get_branches():
                    branch_name = gh_branch.name
                    if gh_branch.name in correct_series:
                        branch = branch_obj.create_or_update_from_name(
                            repository.id, gh_branch.name
                        )
                        branch_ids.append(branch.id)
                    else:
                        repository.organization_id.organization_serie_ids.create_series(
                            branch_name=branch_name, repository=repository
                        )
                        branch = branch_obj.create_or_update_from_name(
                            repository.id, gh_branch.name
                        )
                        branch_ids.append(branch.id)
                repository.repository_branch_ids = [(6, 0, branch_ids)]

    def button_sync_branch(self):
        if self.organization_id.fetch_branches is True:
            self._fetch_all_branches()
        else:
            branch_obj = self.env["github.repository.branch"]
            for repository in self.filtered(lambda r: not r.is_ignored):
                gh_repo = repository.find_related_github_object()
                branch_ids = []
                correct_series = (
                    repository.organization_id.organization_serie_ids.mapped("name")
                )
                for gh_branch in gh_repo.get_branches():
                    if gh_branch.name in correct_series:
                        # We don't use get_from_id_or_create because repository
                        # branches does not have any ids. (very basic object in the
                        # Github API)
                        branch = branch_obj.create_or_update_from_name(
                            repository.id, gh_branch.name
                        )
                        branch_ids.append(branch.id)
                    else:
                        _logger.warning(
                            "the branch '%s'/'%s' has been ignored.",
                            repository.name,
                            gh_branch.name,
                        )
                repository.repository_branch_ids = [(6, 0, branch_ids)]
