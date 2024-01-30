import requests

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    odoo_versions = fields.Char(
        required=True,
        config_parametr="github_connector_odoo.odoo_versions",
    )
    odoo_branches_url = fields.Char(
        config_parametr="github_connector_odoo.odoo_branches_url",
    )

    def get_odoo_versions(self):
        """Compute odoo versions list"""
        odoo_branches_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("github_connector_odoo.odoo_branches_url", False)
        )
        odoo_branches = requests.get(odoo_branches_url, timeout=10).json()
        odoo_versions = [
            item["name"]
            for item in odoo_branches
            if item["name"].replace(".", "").isdigit()
        ]
        versions_list = []
        for i in odoo_versions:
            if "." in i:
                full_version, short_version = i, i.split(".")[0]
                versions_list.extend([full_version, short_version])
            else:
                versions_list.append(i)
        # this is need for remove second 6 version (6.0, 6.1)
        if "6" in versions_list:
            versions_list.remove("6")
        versions_list = ", ".join(versions_list)
        self.env["ir.config_parameter"].set_param(
            "github_connector_odoo.odoo_versions", versions_list
        )
        return versions_list

    def cron_get_odoo_versions(self):
        self.get_odoo_versions()
        return True
