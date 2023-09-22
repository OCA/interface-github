#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestGithubConnectorCommon


class TestBranch(TestGithubConnectorCommon):
    def test_display_name(self):
        """The display name shows
        the Organization name,
        the Repository name
        and the Branch name.
        """
        branch = self.repository_ocb_13
        repository = branch.repository_id
        organization = repository.organization_id

        display_name = branch.display_name
        self.assertIn(branch.name, display_name)
        self.assertIn(repository.name, display_name)
        self.assertIn(organization.github_name, display_name)
