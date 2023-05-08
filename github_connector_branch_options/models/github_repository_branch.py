# Copyright Cetmix OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models

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
    _name = "github.repository.branch"
    _inherit = "github.repository.branch"

    # If name is not equal odoo version, but it is specified there
    series_name = fields.Char(readonly=True, index=True, compute="_compute_series_name")

    def _compute_series_name(self):
        """Defines the series_name for the branch name"""
        for branch in self:
            # get odoo version from branch name
            get_version = branch.name.split("-", 1)[0]
            if get_version in _odoo_version:
                if "." not in list(get_version):
                    get_version += ".0"
                    branch.series_name = get_version
                else:
                    branch.series_name = get_version
            else:
                branch.series_name = "Not defined"

    @api.depends("organization_id", "name")
    def _compute_organization_serie_id(self):
        for branch in self:
            for serie in branch.organization_id.organization_serie_ids:
                if serie.name == branch.name or serie.name == branch.series_name:
                    branch.organization_serie_id = serie
