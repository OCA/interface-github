# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import SavepointCase


class TestGithubConnectorCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.info_keys = [
            "code_count",
            "documentation_count",
            "empty_count",
            "string_count",
            "scanned_files",
        ]
        cls.model_gos = cls.env["github.organization.serie"]
        cls.model_gr = cls.env["github.repository"]
        cls.model_grb = cls.env["github.repository.branch"]
        cls.oca = cls.env.ref("github_connector.oca_organization")
        cls.serie_13 = cls.env.ref("github_connector.oca_organization_serie_13")
        cls.repository_ocb = cls.model_gr.create(
            {
                "name": "OCB",
                "organization_id": cls.oca.id,
                "github_login": "%s/OCB" % cls.oca.github_login,
            }
        )
        cls.repository_interface_github = cls.model_gr.create(
            {
                "name": "interface-github",
                "organization_id": cls.oca.id,
                "github_login": "%s/interface-github" % cls.oca.github_login,
            }
        )
        # repository branch
        cls.repository_ocb_13 = cls.model_grb.create(
            {
                "name": cls.serie_13.name,
                "organization_id": cls.oca.id,
                "repository_id": cls.repository_ocb.id,
                "organization_serie_id": cls.serie_13.id,
            }
        )
        cls.repository_interface_github_13 = cls.model_grb.create(
            {
                "name": cls.serie_13.name,
                "organization_id": cls.oca.id,
                "repository_id": cls.repository_interface_github.id,
                "organization_serie_id": cls.serie_13.id,
            }
        )
        cls._download_and_analyze(cls, cls.repository_interface_github_13)

    def _download_and_analyze(self, repo_branch):
        if repo_branch.state == "to_download":
            repo_branch._download_code()
        repo_branch.analyze_code_one()
