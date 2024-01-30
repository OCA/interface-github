# Copyright Cetmix OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests.common import SavepointCase


class TestGithubRepositoryBranch(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestGithubRepositoryBranch, cls).setUpClass()
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
            {"name": "t1216-test_branch", "repository_id": cls.test_repository.id}
        )

    def test_get_branch_version(self):
        """Testing the function of determining of odoo version by the name of the branch"""
        # branch name contains valid odoo version
        branch_name = "12.0-test_branch-test_module"
        expected_version = "12.0"
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 12.0"
        )

        # branch name does not contain valid odoo version
        branch_name = "t1216-test_branch"
        expected_version = False
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 'False'"
        )

        # branch name contains valid odoo version with decimal point
        branch_name = "6.1_test_branch-test_module"
        expected_version = "6.1"
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 6.1"
        )

        # branch name contains version but not in valid format
        branch_name = "16/0-test_branch"
        expected_version = "16.0"
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 16.0"
        )

        # branch name contains version but not in valid format
        # returns the version in the correct format
        branch_name = "test_branch-16.1"
        expected_version = "16.0"
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 16.0"
        )

        # branch name does not contain version
        exist_versions = self.env["res.config.settings"].get_odoo_versions()
        # find latest avaliable odoo version
        latest_version = exist_versions[-2:]
        branch_name = "test_branch-" + (
            latest_version[:-1] + str(int(latest_version[-1]) + 1)
        )
        expected_version = False
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 'False'"
        )

        # branch name contains valid odoo versions in the middle
        branch_name = "19-test_module-14-test_branch"
        expected_version = "14.0"
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 14.0"
        )

        # branch name contains single valid odoo version
        branch_name = "8.0"
        expected_version = "8.0"
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 8.0"
        )

        # the branch name contains the version not in valid format
        # and specified without a separator before the number
        branch_name = "test_branch_v5"
        expected_version = "5.0"
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 5.0"
        )

        # the branch name contains the version specified without a separator before the number
        branch_name = "test_branch_v13.0-test_module"
        expected_version = "13.0"
        actual_version = self.repository_branch.get_branch_version(branch_name)
        self.assertEqual(
            actual_version, expected_version, msg="actual_version must be 13.0"
        )

    def test_compute_odoo_version(self):
        """Testing compute_odoo_version function"""
        self.assertEqual(
            self.branch_1.odoo_version, "12.0", msg="actual_version must be 12.0"
        )
        self.assertEqual(
            self.branch_2.odoo_version,
            False,
            msg="actual_version must be 'False'",
        )
