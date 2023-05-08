# Copyright Cetmix OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)

_odoo_version = [
    "5.0",
    "6.0",
    "6.1",
    "7.0",
    "8.0",
    "9.0",
    "10.0",
    "11.0",
    "12.0",
    "13.0",
    "14.0",
    "15.0",
    "16.0",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
]


class GithubRepository(models.Model):
    _name = "github.repository"
    _inherit = "github.repository"

    def create_series(self, branch_name=False, repository=False):
        """Create github organization series"""
        branch_serie = branch_name.split("-", 1)[0]
        if "." not in list(branch_serie):
            branch_serie += ".0"
        exist_series = repository.organization_id.organization_serie_ids.mapped("name")
        if branch_serie in _odoo_version and branch_serie not in exist_series:
            sequence = repository.organization_id.organization_serie_ids.mapped(
                "sequence"
            )
            if sequence:
                seq = max(sequence) + 1
            else:
                seq = 1
            repository.organization_id.write(
                {
                    "organization_serie_ids": [
                        (0, 0, {"name": branch_serie, "sequence": seq})
                    ]
                }
            )

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
                        self.create_series(
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
