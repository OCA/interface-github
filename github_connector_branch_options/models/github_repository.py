# Copyright Cetmix OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class GithubRepository(models.Model):
    _name = "github.repository"
    _inherit = "github.repository"

    def create_series(self, branch_name=False, repository=False):
        """Create github organization series"""
        sequence = repository.organization_id.organization_serie_ids.mapped("sequence")
        if sequence:
            seq = max(sequence) + 1
        else:
            seq = 1
        series_name = branch_name.split("-", 1)[0]
        exist_series = repository.organization_id.organization_serie_ids.mapped("name")
        if series_name not in exist_series:
            repository.organization_id.write(
                {
                    "organization_serie_ids": [
                        (0, 0, {"name": series_name, "sequence": seq})
                    ]
                }
            )

    def button_sync_branch(self):
        if self.organization_id.create_series is False:
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
