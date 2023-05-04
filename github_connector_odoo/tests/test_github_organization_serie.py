# Copyright Cetmix OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests.common import SavepointCase


class TestGithubOrganizationSerie(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestGithubOrganizationSerie, cls).setUpClass()
        cls.repository = cls.env["github.repository"]
        cls.organization = cls.env["github.organization"]
        cls.repository_branch = cls.env["github.repository.branch"]
        cls.test_company = cls.organization.create({"name": "Test Company"})
        cls.test_repository = cls.repository.create(
            {
                "name": "repository_1",
                "github_url": "https://github.com/organization/test_repository",
                "organization_id": cls.test_company.id,
            }
        )
        cls.branch_1 = cls.repository_branch.create(
            {
                "name": "12.0-test_branch-test_module",
                "repository_id": cls.test_repository.id,
            }
        )
        cls.branch_2 = cls.repository_branch.create(
            {"name": "12-branch_for_test", "repository_id": cls.test_repository.id}
        )
        cls.branch_3 = cls.repository_branch.create(
            {"name": "t1216-test_branch", "repository_id": cls.test_repository.id}
        )
        cls.branch_4 = cls.repository_branch.create(
            {"name": "14.0-test_branch", "repository_id": cls.test_repository.id}
        )

    def test_create_series(self):
        """Testing create_series function"""
        organization = self.test_company
        self.assertEqual(
            organization.organization_serie_ids.mapped("sequence"),
            [],
            msg="series sequences list must be empty",
        )
        # calling the function for branch with odoo version in the name
        branch = self.branch_1
        repository = self.test_repository
        repository.organization_id.organization_serie_ids.create_series(
            branch_name=branch.name, repository=repository
        )
        branch._compute_organization_serie_id()
        self.assertIn(
            branch.organization_serie_id,
            repository.organization_id.organization_serie_ids,
            msg="branch serie must be added to organization series list",
        )
        # Add branch with the same odoo version
        actual_series_list = repository.organization_id.organization_serie_ids
        branch = self.branch_2
        repository = self.test_repository
        repository.organization_id.organization_serie_ids.create_series(
            branch_name=branch.name, repository=repository
        )
        self.assertEqual(
            actual_series_list,
            repository.organization_id.organization_serie_ids,
            msg="new branch serie must not be created",
        )
        # add branch without odoo version in the name, the series should not be created
        branch = self.branch_3
        repository.organization_id.organization_serie_ids.create_series(
            branch_name=branch.name, repository=repository
        )
        self.assertEqual(
            actual_series_list,
            repository.organization_id.organization_serie_ids,
            msg="organization series list must not be changed",
        )
        # Add new branch
        branch = self.branch_4
        repository = self.test_repository
        repository.organization_id.organization_serie_ids.create_series(
            branch_name=branch.name, repository=repository
        )
        branch._compute_organization_serie_id()
        self.assertIn(
            branch.organization_serie_id,
            repository.organization_id.organization_serie_ids,
            msg="new branch serie must be created",
        )
        # Check sequence number
        self.assertEqual(
            organization.organization_serie_ids.mapped("sequence"),
            [1, 2],
            msg="Two series must be created",
        )
