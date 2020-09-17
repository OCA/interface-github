# Copyright 2021-2022 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

import responses

from odoo.modules.module import get_resource_path

from .common import TestGithubConnectorCommon


class TestGithubConnector(TestGithubConnectorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create appropriate responses for the API calls
        with open(
            get_resource_path(
                "github_connector",
                "tests",
                "res",
                "github_user_OCA-git-bot_response.json",
            )
        ) as jsonfile:
            cls.user_data = json.loads(jsonfile.read())
        responses.add(
            responses.GET,
            "https://api.github.com:443/users/OCA-git-bot",
            json=cls.user_data,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.github.com:443/user/8723280",
            json=cls.user_data,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.github.com:443/orgs/OCA-git-bot",
            json={
                "message": "Not Found",
            },
            status=404,
        )

    @responses.activate
    def test_partner_get_from_id_or_create(self):
        partner_model = self.env["res.partner"]
        partner = partner_model.create_from_name("OCA-git-bot")
        self.assertEqual(partner.github_name, "OCA-git-bot")
        # Check create process not really create new record
        res = partner_model.get_from_id_or_create(data={"login": "OCA-git-bot"})
        self.assertEqual(partner.id, res.id)
        # Try to archive record and try to create again
        partner.active = False
        res = partner_model.get_from_id_or_create(data={"login": "OCA-git-bot"})
        self.assertEqual(partner.id, res.id)
