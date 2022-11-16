# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# Copyright 2021 Tecnativa - João Marques
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class GithubRepository(models.Model):
    _name = "github.repository"
    _inherit = ["abstract.github.model"]
    _order = "organization_id, name"
    _description = "Github Repository"

    _github_login_field = "full_name"

    # Column Section
    organization_id = fields.Many2one(
        comodel_name="github.organization",
        string="Organization",
        required=True,
        index=True,
        readonly=True,
        ondelete="cascade",
    )

    name = fields.Char(index=True, required=True, readonly=True)

    complete_name = fields.Char(
        readonly=True,
        compute="_compute_complete_name",
        store=True,
    )

    description = fields.Char(readonly=True)

    website = fields.Char(readonly=True)

    repository_branch_ids = fields.One2many(
        comodel_name="github.repository.branch",
        inverse_name="repository_id",
        string="Branches",
        readonly=True,
    )

    repository_branch_qty = fields.Integer(
        string="Number of Branches",
        compute="_compute_repository_branch_qty",
        store=True,
    )

    team_ids = fields.One2many(
        string="Teams",
        comodel_name="github.team.repository",
        inverse_name="repository_id",
        readonly=True,
    )

    team_qty = fields.Integer(
        string="Number of Teams", compute="_compute_team_qty", store=True
    )

    is_ignored = fields.Boolean(
        compute="_compute_ignore",
        help="If checked, the branches will not be synchronized, and the"
        " code source will this way not be downloaded and analyzed. To ignore"
        " a repository, go to the organization and add the file"
        " 'Ignored Repositories'.",
    )

    color = fields.Integer(string="Color Index", compute="_compute_ignore")
    analysis_rule_ids = fields.Many2many(
        string="Analysis Rules", comodel_name="github.analysis.rule"
    )

    # Compute Section
    @api.depends("organization_id.ignored_repository_names")
    def _compute_ignore(self):
        for repository in self:
            ignored_txt = repository.organization_id.ignored_repository_names
            repository.is_ignored = (
                ignored_txt and repository.name in ignored_txt.split("\n")
            )
            repository.color = repository.is_ignored and 1 or 0

    @api.depends("team_ids")
    def _compute_team_qty(self):
        data = self.env["github.team.repository"].read_group(
            [("repository_id", "in", self.ids)], ["repository_id"], ["repository_id"]
        )
        mapping = {
            data["repository_id"][0]: data["repository_id_count"] for data in data
        }
        for item in self:
            item.team_qty = mapping.get(item.id, 0)

    @api.depends("name", "organization_id.github_name")
    def _compute_complete_name(self):
        for repository in self:
            repository.complete_name = "%(login)s/%(rep_name)s" % (
                {
                    "login": repository.organization_id.github_name,
                    "rep_name": repository.name or "",
                }
            )

    @api.depends("repository_branch_ids.repository_id")
    def _compute_repository_branch_qty(self):
        data = self.env["github.repository.branch"].read_group(
            [("repository_id", "in", self.ids)], ["repository_id"], ["repository_id"]
        )
        mapping = {
            data["repository_id"][0]: data["repository_id_count"] for data in data
        }
        for item in self:
            item.repository_branch_qty = mapping.get(item.id, 0)

    # Overloadable Section
    @api.model
    def get_conversion_dict(self):
        res = super().get_conversion_dict()
        res.update(
            {
                "name": "name",
                "description": "description",
                "website": "homepage",
            }
        )
        return res

    @api.model
    def get_odoo_data_from_github(self, gh_data):
        res = super().get_odoo_data_from_github(gh_data)
        org_id = self.env.context.get("github_organization_id", None)
        if not org_id:
            # Fetch current organization object
            organization_obj = self.env["github.organization"]
            organization = organization_obj.get_from_id_or_create(gh_data=gh_data.owner)
            org_id = organization.id
        res.update({"organization_id": org_id})
        return res

    def find_related_github_object(self, obj_id=None):
        """Query Github API to find the related object"""
        gh_api = self.get_github_connector()
        return gh_api.get_repo(int(obj_id or self.github_id_external))

    def get_github_base_obj_for_creation(self):
        self.ensure_one()
        gh_api = self.get_github_connector()
        return gh_api.get_organization(self.organization_id.github_name)

    def create_in_github(self):
        """Create an object in Github through the API"""
        self.ensure_one()
        # Create in Github
        gh_base_obj = self.get_github_base_obj_for_creation()
        gh_repo = gh_base_obj.create_repo(
            name=self.name, description=self.description or "", homepage=self.website
        )
        # Create in Odoo with the returned data and update object
        data = self.get_odoo_data_from_github(gh_repo)
        new_item = self._create_from_github_data(data)
        new_item.full_update()
        new_item._hook_after_github_creation()
        return new_item

    def full_update(self):
        self.button_sync_branch()

    @api.model
    def cron_update_branch_list(self):
        branches = self.search([])
        branches.button_sync_branch()
        return True

    def button_sync_branch(self):
        branch_obj = self.env["github.repository.branch"]
        for repository in self.filtered(lambda r: not r.is_ignored):
            gh_repo = repository.find_related_github_object()
            branch_ids = []
            correct_series = repository.organization_id.organization_serie_ids.mapped(
                "name"
            )
            for gh_branch in gh_repo.get_branches():
                if gh_branch.name in correct_series:
                    # We don't use get_from_id_or_create because repository
                    # branches does not have any ids. (very basic object in the
                    # Github API)
                    branch = branch_obj.create_or_update_from_name(
                        repository.id, gh_branch.name
                    )
                    branch_ids.append(branch.id)
                else:
                    _logger.warning(
                        "the branch '%s'/'%s' has been ignored.",
                        repository.name,
                        gh_branch.name,
                    )
            repository.repository_branch_ids = [(6, 0, branch_ids)]

    def action_github_team_repository_from_repository(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector.action_github_team_repository_from_repository"
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_repository_id"] = self.id
        return action

    def action_github_repository_branch(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector.action_github_repository_branch"
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_repository_id"] = self.id
        return action
