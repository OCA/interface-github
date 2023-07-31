#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

import responses

from odoo.modules import get_resource_path

from odoo.addons.github_connector.tests.common import TestGithubConnectorCommon


class TestCommon(TestGithubConnectorCommon):
    @classmethod
    def _add_response(
        cls,
        method=responses.GET,
        url=None,
        status=200,
        module="github_connector_pull_request",
        file_name=None,
    ):
        with open(
            get_resource_path(
                module,
                "tests",
                "data",
                file_name,
            )
        ) as jsonfile:
            responses.add(
                method=method,
                url=url,
                json=json.loads(jsonfile.read()),
                status=status,
            )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._add_response(
            url="https://api.github.com:443/users/OCA",
            file_name="user.json",
        )
        cls._add_response(
            url="https://api.github.com:443/repositories/70173147",
            file_name="repo.json",
        )
        cls._add_response(
            url="https://api.github.com:443/repos/OCA/interface-github",
            file_name="repo.json",
        )
        cls._add_response(
            url="https://api.github.com:443/repos/OCA/interface-github/pulls",
            file_name="pulls.json",
        )
        cls._add_response(
            url="https://api.github.com:443/repos/OCA/interface-github/pulls/107",
            file_name="pull107.json",
        )
        cls._add_response(
            url="https://api.github.com:443/repos/OCA/interface-github/pulls/103",
            file_name="pull103.json",
        )
