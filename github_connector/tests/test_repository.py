#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestGithubConnectorCommon


class TestRepository(TestGithubConnectorCommon):
    def test_display_name(self):
        """The display name shows
        the Organization name
        and the Repository name.
        """
        repository = self.repository_ocb
        organization = repository.organization_id

        display_name = repository.display_name
        self.assertIn(repository.name, display_name)
        self.assertIn(organization.github_name, display_name)
