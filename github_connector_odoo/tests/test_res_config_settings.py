# Copyright Cetmix OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests.common import SavepointCase


class TestResConfigSettings(SavepointCase):
    def test_get_odoo_versions(self):
        """Testing get_odoo_versions function"""
        # Check defaul odoo version values
        odoo_versions = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("github_connector_odoo.odoo_versions")
        )
        self.assertEqual(
            odoo_versions, False, msg="before 1st branch sync must be empty"
        )
        versions_list = self.env["res.config.settings"].get_odoo_versions()
        odoo_versions = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("github_connector_odoo.odoo_versions")
        )
        self.assertEqual(
            odoo_versions,
            versions_list,
            msg="all versions must be added",
        )

    def test_cron_get_odoo_versions(self):
        odoo_versions = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("github_connector_odoo.odoo_versions")
        )
        self.assertEqual(
            odoo_versions, False, msg="before 1st branch sync must be empty"
        )
        self.env["res.config.settings"].cron_get_odoo_versions()
        odoo_versions = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("github_connector_odoo.odoo_versions")
        )
        self.assertTrue(
            odoo_versions,
            msg="versions must be added",
        )
