#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from urllib.parse import urlparse

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class GithubPullRequest(models.Model):
    _name = "github.pull_request"
    _inherit = "abstract.github.model"
    _description = "GitHub Pull Request"

    _github_login_field = "html_url"

    name = fields.Char(string="Number", required=True)
    repository_id = fields.Many2one(
        comodel_name="github.repository",
        string="Github Repository",
        required=True,
    )
    user = fields.Char()
    title = fields.Char()
    state = fields.Char()
    description = fields.Text()
    base_ref = fields.Char(string="Base Ref")
    base_url = fields.Char(string="Base URL")
    head_ref = fields.Char(string="Head Ref")
    head_url = fields.Char(string="Head URL")

    @api.model
    def _get_repository(self, pull_request_url):
        parsed_url = urlparse(pull_request_url)
        url_path = parsed_url.path
        # The login field of repository is its full name, like OCA/interface-github
        repo_full_name_matches = re.findall(r"/(.*)/pull.*", url_path)
        if not repo_full_name_matches:
            raise UserError(
                _(
                    "Pull Request URL %(pr_url)s cannot be parsed",
                    pr_url=pull_request_url,
                )
            )

        repo_full_name = repo_full_name_matches[0]
        repository = self.env["github.repository"].create_from_name(repo_full_name)
        return repository

    @api.model
    def _get_github_pull_request(self, pull_request_url):
        repository_id = self.env.context.get("repository_id", False)
        if repository_id:
            repository = self.env["github.repository"].browse(repository_id)
        else:
            repository = self._get_repository(pull_request_url)

        gh_repository = repository.find_related_github_object()
        pull_request_number = pull_request_url.split("/")[-1]
        gh_pull_request = gh_repository.get_pull(int(pull_request_number))
        return gh_pull_request

    @api.model
    def get_conversion_dict(self):
        res = super().get_conversion_dict()
        res.update(
            {
                "name": "number",
                "title": "title",
                "description": "body",
                "state": "state",
            }
        )
        return res

    @api.model
    def get_odoo_data_from_github(self, gh_pull_request):
        res = super().get_odoo_data_from_github(gh_pull_request)
        repository_id = self.env.context.get("repository_id", None)
        if repository_id:
            repository = self.env["github.repository"].browse(repository_id)
        else:
            repository = self._get_repository(gh_pull_request.html_url)
        res.update(
            {
                "repository_id": repository.id,
                "user": gh_pull_request.user.login,
                "base_ref": gh_pull_request.head.ref,
                "base_url": f"{gh_pull_request.base.repo.html_url}"
                f"/tree/{gh_pull_request.base.ref}",
                "head_ref": gh_pull_request.head.ref,
                "head_url": f"{gh_pull_request.head.repo.html_url}"
                f"/tree/{gh_pull_request.head.ref}",
            }
        )
        return res

    def find_related_github_object(self, obj_id=None):
        """Query GitHub API to find the related object"""
        self.ensure_one()
        repository = self.repository_id
        return self.with_context(
            repository_id=repository.id,
        )._get_github_pull_request(obj_id or self.github_name)

    @api.model
    def create_from_name(self, pr_url):
        gh_pull_request = self._get_github_pull_request(pr_url)
        if not gh_pull_request:
            raise UserError(
                _(
                    "Pull Request %s not found",
                    pr_url,
                )
            )

        pull_request_values = self.get_odoo_data_from_github(gh_pull_request)
        pull_request = self.with_context(active_test=False).search(
            [
                ("github_id_external", "=", pull_request_values["github_id_external"]),
            ],
            limit=1,
        )
        if not pull_request:
            pull_request = self._create_from_github_data(pull_request_values)
        return pull_request
