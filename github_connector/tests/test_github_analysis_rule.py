# Copyright 2020-2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from .common import TestGithubConnectorCommon


class TestGithubConnectorAnalysisRule(TestGithubConnectorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_group = cls.env.ref(
            "github_connector.github_analysis_rule_group_1_demo"
        )
        cls.rule_python = cls.env.ref("github_connector.github_analysis_rule_python")
        cls.rule_xml = cls.env.ref("github_connector.github_analysis_rule_xml")
        cls.rule_js = cls.env.ref("github_connector.github_analysis_rule_js")
        cls.rule_test = cls.env.ref("github_connector.github_analysis_rule_test")
        cls.rule_ocb = cls.env["github.analysis.rule"].create(
            {
                "name": "OCB files (.py + .xml)",
                "group_id": cls.rule_group.id,
                "paths": """
                *.py
                *.xml
                !/.*/
                """,
            }
        )
        cls.rule_custom = cls.env["github.analysis.rule"].create(
            {
                "name": "Custom",
                "group_id": cls.rule_group.id,
                "paths": """/custom/*.py""",
            }
        )
        cls.oca.write(
            {
                "analysis_rule_ids": [
                    (6, 0, [cls.rule_python.id, cls.rule_xml.id, cls.rule_js.id])
                ]
            }
        )
        cls.repository_ocb.write({"analysis_rule_ids": [(6, 0, cls.rule_ocb.ids)]})
        cls.repository_interface_github_13.write(
            {"analysis_rule_ids": [(6, 0, cls.rule_custom.ids)]}
        )
        cls.repo_branch_item = cls.repository_interface_github_13
        # analyze_code again
        cls._download_and_analyze(cls, cls.repo_branch_item)

    def test_analysis_rule_info(self):
        self.assertEqual(len(self.oca.analysis_rule_ids), 3)
        self.assertEqual(len(self.repository_ocb.analysis_rule_ids), 1)
        self.assertEqual(len(self.repo_branch_item.analysis_rule_info_ids), 4)

    def test_analysis_rule_info_python(self):
        rule_info = self.repo_branch_item.analysis_rule_info_ids.filtered(
            lambda x: x.analysis_rule_id.id == self.rule_python.id
        )
        for info_key in self.info_keys:
            self.assertGreater(rule_info[info_key], 0)

    def test_analysis_rule_info_xml(self):
        rule_info = self.repo_branch_item.analysis_rule_info_ids.filtered(
            lambda x: x.analysis_rule_id.id == self.rule_xml.id
        )
        for info_key in self.info_keys:
            if info_key in ("empty_count", "string_count"):
                self.assertEqual(rule_info[info_key], 0)
            else:
                self.assertGreater(rule_info[info_key], 0)

    def test_analysis_rule_info_js(self):
        rule_info = self.repo_branch_item.analysis_rule_info_ids.filtered(
            lambda x: x.analysis_rule_id.id == self.rule_js.id
        )
        for info_key in self.info_keys:
            self.assertEqual(rule_info[info_key], 0)
