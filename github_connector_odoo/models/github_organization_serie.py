# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class GithubOrganizationSerie(models.Model):
    _inherit = "github.organization.serie"

    def create_series(self, branch_name=False, repository=False):
        """Create github organization serie
        Args:
            branch_name - name of the synchronized branch
            repository - synchronized repository
        """
        get_version = self.env["github.repository.branch"].get_branch_version(
            branch_name=branch_name,
        )
        exist_series = repository.organization_id.organization_serie_ids.mapped("name")
        if get_version and get_version not in exist_series:
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
                        (0, 0, {"name": get_version, "sequence": seq})
                    ]
                }
            )
