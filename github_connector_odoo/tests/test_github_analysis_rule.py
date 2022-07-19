# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.github_connector.tests.common import TestGithubConnectorCommon


class TestGithubConnectorOdooAnalysisRule(TestGithubConnectorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_has_odoo_addons = cls.env.ref(
            "github_connector_odoo.github_analysis_rule_python_has_odoo_addons"
        )
        cls.repository_interface_github_13.write(
            {"analysis_rule_ids": [(6, 0, cls.rule_has_odoo_addons.ids)]}
        )
        cls.repo_branch_item = cls.repository_interface_github_13
        # analyze_code again
        cls._download_and_analyze(cls, cls.repo_branch_item)

    def test_github_module_version_analysis_rule_info(self):
        info_ids = self.repo_branch_item.module_version_analysis_rule_info_ids
        self.assertTrue(
            self.rule_has_odoo_addons.id in info_ids.mapped("analysis_rule_id").ids
        )
        version_item_info = info_ids.filtered(
            lambda x: x.module_version_id.technical_name == "github_connector_odoo"
        )
        for info_key in self.info_keys:
            self.assertGreater(version_item_info[info_key], 0)
        # Check analysis_rule_info_ids in module.version
        verion_item = self.repo_branch_item.module_version_ids.filtered(
            lambda x: x.technical_name == "github_connector_odoo"
        )
        for info_key in self.info_keys:
            self.assertGreater(verion_item.analysis_rule_info_ids[info_key], 0)
