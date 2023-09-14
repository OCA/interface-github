# Copyright 2020-2022 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import json

import responses

from odoo.modules.module import get_resource_path

from .common import TestGithubConnectorCommon


class TestGithubConnectorAnalysisRuleBase(TestGithubConnectorCommon):
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
        # Create appropriate responses for the API calls
        cls._set_github_responses(cls)

    def _set_github_responses(self):
        for github_id in self.oca.mapped("repository_ids.github_id_external"):
            with open(
                get_resource_path(
                    "github_connector",
                    "tests",
                    "res",
                    "github_repo_%s_response.json" % github_id,
                )
            ) as jsonfile:
                responses.add(
                    responses.GET,
                    "https://api.github.com:443/repositories/%s" % github_id,
                    json=json.loads(jsonfile.read()),
                    status=200,
                )


class TestGithubConnectorAnalysisRule(TestGithubConnectorAnalysisRuleBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._download_and_analyze(cls, cls.repo_branch_item)

    def test_analysis_rule_info(self):
        self.assertEqual(len(self.oca.analysis_rule_ids), 3)
        self.assertEqual(len(self.repository_ocb.analysis_rule_ids), 1)
        self.assertEqual(len(self.repo_branch_item.analysis_rule_info_ids), 4)

    def test_inhibit_analysis_rule_info_01(self):
        # Rules available from repository branch
        rules = self.repo_branch_item._get_analysis_rules()
        self.assertIn(self.rule_custom, rules)
        self.assertNotIn(self.rule_ocb, rules)
        self.assertIn(self.rule_python, rules)
        self.assertIn(self.rule_xml, rules)
        self.assertIn(self.rule_js, rules)
        # Rules from OCB repository
        rules = self.repository_ocb._get_analysis_rules()
        self.assertNotIn(self.rule_custom, rules)
        self.assertIn(self.rule_ocb, rules)
        self.assertIn(self.rule_python, rules)
        self.assertIn(self.rule_xml, rules)
        self.assertIn(self.rule_js, rules)
        # Rules from interface-gitbub repository
        rules = self.repository_interface_github._get_analysis_rules()
        self.assertNotIn(self.rule_custom, rules)
        self.assertNotIn(self.rule_ocb, rules)
        self.assertIn(self.rule_python, rules)
        self.assertIn(self.rule_xml, rules)
        self.assertIn(self.rule_js, rules)

    def test_inhibit_analysis_rule_info_02(self):
        # Only repository branch rule available
        self.repo_branch_item.inhibit_inherited_rules = True
        rules = self.repo_branch_item._get_analysis_rules()
        self.assertIn(self.rule_custom, rules)
        self.assertNotIn(self.rule_ocb, rules)
        self.assertNotIn(self.rule_python, rules)
        self.assertNotIn(self.rule_xml, rules)
        self.assertNotIn(self.rule_js, rules)
        # Remove rule from repository branch
        self.repo_branch_item.analysis_rule_ids = [(5, 0, 0)]
        rules = self.repo_branch_item._get_analysis_rules()
        self.assertNotIn(self.rule_custom, rules)
        self.assertNotIn(self.rule_ocb, rules)
        self.assertNotIn(self.rule_python, rules)
        self.assertNotIn(self.rule_xml, rules)
        self.assertNotIn(self.rule_js, rules)

    def test_inhibit_analysis_rule_info_03(self):
        # Only repository rules available
        self.repo_branch_item.analysis_rule_ids = [(5, 0, 0)]
        self.repository_interface_github.write(
            {
                "inhibit_inherited_rules": True,
                "analysis_rule_ids": [(6, 0, self.rule_custom.ids)],
            }
        )
        rules = self.repo_branch_item._get_analysis_rules()
        self.assertIn(self.rule_custom, rules)
        self.assertNotIn(self.rule_ocb, rules)
        self.assertNotIn(self.rule_python, rules)
        self.assertNotIn(self.rule_xml, rules)
        self.assertNotIn(self.rule_js, rules)
        # Remove rules from repository branch
        self.repository_interface_github.analysis_rule_ids = [(5, 0, 0)]
        rules = self.repo_branch_item._get_analysis_rules()
        self.assertNotIn(self.rule_custom, rules)
        self.assertNotIn(self.rule_ocb, rules)
        self.assertNotIn(self.rule_python, rules)
        self.assertNotIn(self.rule_xml, rules)
        self.assertNotIn(self.rule_js, rules)

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
            if info_key == "empty_count":
                self.assertEqual(rule_info[info_key], 0)
            else:
                self.assertGreater(rule_info[info_key], 0)

    def test_analysis_rule_info_js(self):
        rule_info = self.repo_branch_item.analysis_rule_info_ids.filtered(
            lambda x: x.analysis_rule_id.id == self.rule_js.id
        )
        for info_key in self.info_keys:
            self.assertEqual(rule_info[info_key], 0)
