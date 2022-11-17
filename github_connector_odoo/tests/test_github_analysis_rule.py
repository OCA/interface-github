# Copyright 2021-2022 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import responses

from odoo.modules.module import get_resource_path

from odoo.addons.github_connector.tests.test_github_analysis_rule import (
    TestGithubConnectorAnalysisRuleBase,
)


class TestGithubConnectorOdooAnalysisRule(TestGithubConnectorAnalysisRuleBase):
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
        cls._download_and_analyze(cls, cls.repo_branch_item)

    def _set_github_responses(self):
        res = super()._set_github_responses(self)
        with open(
            get_resource_path(
                "github_connector_odoo",
                "tests",
                "res",
                "github_maintainer_tools_repos_with_ids.txt",
            )
        ) as test_file:
            domain = "https://raw.githubusercontent.com"
            responses.add(
                responses.GET,
                "%s/OCA/maintainer-tools/master/tools/repos_with_ids.txt" % domain,
                json=test_file.read(),
                status=200,
            )
        return res

    def test_github_module_version_analysis_rule_info(self):
        info_ids = self.repo_branch_item.module_version_analysis_rule_info_ids
        self.assertTrue(
            self.rule_has_odoo_addons.id in info_ids.mapped("analysis_rule_id").ids
        )
        version_item_info = info_ids.filtered(
            lambda x: x.module_version_id.technical_name == "github_connector_odoo"
        )
        for info_key in self.info_keys:
            self.assertGreater(version_item_info[info_key], 0, info_key)
        # Check analysis_rule_info_ids in module.version
        verion_item = self.repo_branch_item.module_version_ids.filtered(
            lambda x: x.technical_name == "github_connector_odoo"
        )
        for info_key in self.info_keys:
            self.assertGreater(verion_item.analysis_rule_info_ids[info_key], 0)
