#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import responses

from .common import TestCommon


class TestRepository(TestCommon):
    @responses.activate
    def test_sync_pull_request(self):
        """Load Pull Requests of a Repository."""
        # Arrange
        repository = self.repository_interface_github
        # pre-condition
        self.assertFalse(repository.pull_request_ids)

        # Act
        repository.button_sync_pull_request()

        # Assert
        pull_requests = repository.pull_request_ids
        self.assertEqual(len(pull_requests), 2)
        self.assertCountEqual(pull_requests.mapped("name"), ["103", "107"])

        # Act: Sync again, with CRON
        cron = self.env.ref("github_connector_pull_request.ir_cron_sync_pull_requests")
        cron.method_direct_trigger()

        # Assert: Another sync does not create new objects
        new_pull_requests = repository.pull_request_ids
        self.assertEqual(new_pull_requests, pull_requests)
