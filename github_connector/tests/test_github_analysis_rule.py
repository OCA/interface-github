# Copyright 2020 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import json

import responses

from odoo.modules.module import get_resource_path
from odoo.tests.common import SavepointCase


class TestGithubAnalysisRule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analysis_rule_group_misc = cls.env["github.analysis.rule.group"].create(
            {"name": "Misc"}
        )
        cls.analysis_rule_python = cls.env["github.analysis.rule"].create(
            {
                "name": "Python files",
                "group_id": cls.analysis_rule_group_misc.id,
                "paths": "**/account_analytic_project/**/*.py",
            }
        )
        cls.analysis_rule_xml = cls.env["github.analysis.rule"].create(
            {
                "name": "Xml files",
                "group_id": cls.analysis_rule_group_misc.id,
                "paths": "**/account_analytic_project/**/*.xml",
            }
        )
        cls.analysis_rule_js = cls.env["github.analysis.rule"].create(
            {
                "name": "Js files",
                "group_id": cls.analysis_rule_group_misc.id,
                "paths": "**/account_analytic_project/**/*.js",
            }
        )
        cls.analysis_rule_test = cls.env["github.analysis.rule"].create(
            {
                "name": "Test files",
                "group_id": cls.analysis_rule_group_misc.id,
                "paths": "/tests/*.py",
            }
        )
        cls.analysis_rule_ocb = cls.env["github.analysis.rule"].create(
            {
                "name": "OCB files (.py + .xml)",
                "group_id": cls.analysis_rule_group_misc.id,
                "paths": """
                *.py
                *.xml
                !/.*/
                """,
            }
        )
        cls.analysis_rule_custom = cls.env["github.analysis.rule"].create(
            {
                "name": "Custom",
                "group_id": cls.analysis_rule_group_misc.id,
                "paths": """/custom/*.py""",
            }
        )
        cls.organization_oca = cls.env["github.organization"].create(
            {
                "name": "Odoo Community Association",
                "description": "The GitHub repos for all Open Source work around Odoo",
                "website_url": "https://odoo-community.org/",
                "github_url": "https://github.com/OCA",
                "github_name": "OCA",
                "github_id_external": 7600578,
                "analysis_rule_ids": [
                    (4, cls.analysis_rule_python.id),
                    (4, cls.analysis_rule_xml.id),
                    (4, cls.analysis_rule_js.id),
                ],
            }
        )
        cls.organization_serie_6 = cls.env["github.organization.serie"].create(
            {"organization_id": cls.organization_oca.id, "sequence": 6, "name": "6.1"}
        )
        cls.organization_serie_13 = cls.env["github.organization.serie"].create(
            {"organization_id": cls.organization_oca.id, "sequence": 13, "name": "13.0"}
        )
        cls.repository_ocb = cls.env["github.repository"].create(
            {
                "name": "OCB",
                "organization_id": cls.organization_oca.id,
                "github_name": "%s/OCB" % cls.organization_oca.github_name,
                "github_id_external": 20558462,
                "analysis_rule_ids": [(4, cls.analysis_rule_ocb.id)],
            }
        )
        cls.repository_account_analytic = cls.env["github.repository"].create(
            {
                "name": "account-analytic",
                "organization_id": cls.organization_oca.id,
                "github_id_external": 20881668,
                "github_name": "%s/account-analytic" % cls.organization_oca.github_name,
            }
        )
        # repository branch
        cls.repository_ocb_branch_13 = cls.env["github.repository.branch"].create(
            {
                "name": cls.organization_serie_13.name,
                "organization_id": cls.organization_oca.id,
                "repository_id": cls.repository_ocb.id,
                "organization_serie_id": cls.organization_serie_13.id,
            }
        )
        cls.repository_account_analytic_branch_6 = cls.env[
            "github.repository.branch"
        ].create(
            {
                "name": cls.organization_serie_6.name,
                "organization_id": cls.organization_oca.id,
                "repository_id": cls.repository_account_analytic.id,
                "organization_serie_id": cls.organization_serie_6.id,
                "analysis_rule_ids": [(4, cls.analysis_rule_custom.id)],
            }
        )
        cls.env["ir.config_parameter"].set_param("github.access_token", "test")
        # Create appropriate responses for the API calls
        with open(
            get_resource_path(
                "github_connector", "tests", "res", "github_repo_20881668_response.json"
            )
        ) as jsonfile:
            cls.repo_data = json.loads(jsonfile.read())
        responses.add(
            responses.GET,
            "https://api.github.com:443/repositories/20881668",
            json=cls.repo_data,
            status=200,
        )

    @responses.activate
    def test_github_analysis_rule(self):
        self.assertEqual(len(self.organization_oca.analysis_rule_ids), 3)
        self.assertEqual(len(self.repository_ocb.analysis_rule_ids), 1)
        # download + analyze_code
        self.repository_account_analytic_branch_6._download_code()
        self.repository_account_analytic_branch_6.analyze_code_one()
        # info ids
        info_ids = self.repository_account_analytic_branch_6.analysis_rule_info_ids
        self.assertEqual(len(info_ids), 4)
        # python info
        python_info = info_ids.filtered(
            lambda x: x.analysis_rule_id.id == self.analysis_rule_python.id
        )
        self.assertEqual(python_info.code_count, 60)
        self.assertEqual(python_info.documentation_count, 106)
        self.assertEqual(python_info.empty_count, 20)
        self.assertEqual(python_info.string_count, 19)
        self.assertEqual(python_info.scanned_files, 4)
        # xml info
        xml_info = info_ids.filtered(
            lambda x: x.analysis_rule_id.id == self.analysis_rule_xml.id
        )
        self.assertEqual(xml_info.code_count, 35)
        self.assertEqual(xml_info.documentation_count, 0)
        self.assertEqual(xml_info.empty_count, 0)
        self.assertEqual(xml_info.string_count, 10)
        self.assertEqual(xml_info.scanned_files, 1)
        # js info
        js_info = info_ids.filtered(
            lambda x: x.analysis_rule_id.id == self.analysis_rule_js.id
        )
        self.assertEqual(js_info.code_count, 0)
        self.assertEqual(js_info.documentation_count, 0)
        self.assertEqual(js_info.empty_count, 0)
        self.assertEqual(js_info.string_count, 0)
        self.assertEqual(js_info.scanned_files, 0)
