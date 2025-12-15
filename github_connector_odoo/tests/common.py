# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools import convert_file


class GithubConnectorOdooDemoMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        for demo_file in [
            "demo/github_analysis_rule_group_demo.xml",
            "demo/github_analysis_rule_demo.xml",
            "demo/github_organization.xml",
        ]:
            convert_file(
                cls.env,
                "github_connector_odoo",
                demo_file,
                {},
                "init",
                False,
            )
