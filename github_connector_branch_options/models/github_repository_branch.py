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
    serie_name = fields.Char(readonly=True, index=True, compute="_compute_serie_name")

    def _compute_serie_name(self):
        """Defines the series_name for the branch name"""
        for branch in self:
            split_name = branch.name.split("-")
            # get odoo version from branch name
            for i in split_name:
                if i in _odoo_version:
                    # if odoo version is written without '.0'
                    if "." not in list(i):
                        i += ".0"
                        branch.serie_name = i
                    else:
                        branch.serie_name = i
                    break
                else:
                    branch.serie_name = "Not defined"

    @api.depends("organization_id", "name")
    def _compute_organization_serie_id(self):
        for branch in self:
            for serie in branch.organization_id.organization_serie_ids:
                if serie.name == branch.name or serie.name == branch.serie_name:
                    branch.organization_serie_id = serie
