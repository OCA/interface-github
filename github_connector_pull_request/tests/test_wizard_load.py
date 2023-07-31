#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import responses

from .common import TestCommon


class TestWizardLoad(TestCommon):
    @responses.activate
    def test_sync_pull_request(self):
        wizard = self.env["wizard.load.github.model"].create(
            {
                "github_type": "pr",
                "name": "https://github.com/OCA/interface-github/pull/103",
            },
        )
        self.assertFalse(
            self.env["github.pull_request"].search(
                [
                    ("name", "=", "103"),
                ]
            )
        )

        wizard.button_create_from_github()

        self.assertTrue(
            self.env["github.pull_request"].search(
                [
                    ("name", "=", "103"),
                ]
            )
        )
