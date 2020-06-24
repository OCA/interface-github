# Copyright 2018 Road-Support - Roel Adriaans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OdooModuleVersion(models.Model):
    _inherit = "odoo.module.version"

    _ODOO_DEVELOPMENT_STATUS_SELECTION = [
        ("alpha", "Alpha"),
        ("beta", "Beta"),
        ("production/stable", "Production/Stable"),
        ("mature", "Mature"),
    ]

    development_status = fields.Selection(
        string="Module maturity",
        selection=_ODOO_DEVELOPMENT_STATUS_SELECTION,
        readonly=True,
    )

    @api.model
    def manifest_2_odoo(self, info, repository_branch, module):
        res = super(OdooModuleVersion, self).manifest_2_odoo(
            info, repository_branch, module
        )
        if "development_status" in info:
            res["development_status"] = info["development_status"].lower()
        return res
