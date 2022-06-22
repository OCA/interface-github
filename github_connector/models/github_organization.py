# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# Copyright 2020 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - João Marques
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from github.GithubException import GithubException

from odoo import _, api, exceptions, fields, models


class GithubOrganization(models.Model):
    _name = "github.organization"
    _inherit = ["abstract.github.model"]
    _order = "name"
    _description = "Github organization"

    _github_login_field = "login"

    # Columns Section
    name = fields.Char(string="Organization Name", required=True, readonly=True)

    image = fields.Image(readonly=True)

    description = fields.Char(readonly=True)

    email = fields.Char(readonly=True)

    website_url = fields.Char(readonly=True)

    location = fields.Char(readonly=True)

    ignored_repository_names = fields.Text(
        string="Ignored Repositories",
        help="Set here repository names"
        " you want to ignore. One repository per line."
        " If set, the repositories will be created, but branches"
        " synchronization and source code download will be disabled."
        " Exemple:\n"
        "purchase-workflow\nOCB\nOpenUpgrade\n",
    )

    member_ids = fields.Many2many(
        string="Members",
        comodel_name="res.partner",
        relation="github_organization_partner_rel",
        column1="organization_id",
        column2="partner_id",
        readonly=True,
    )

    member_qty = fields.Integer(
        string="Number of Members", compute="_compute_member_qty", store=True
    )

    repository_ids = fields.One2many(
        string="Repositories",
        comodel_name="github.repository",
        inverse_name="organization_id",
        readonly=True,
    )

    repository_qty = fields.Integer(
        string="Number of Repositories", compute="_compute_repository_qty", store=True
    )

    team_ids = fields.One2many(
        string="Teams",
        comodel_name="github.team",
        inverse_name="organization_id",
        readonly=True,
    )

    team_qty = fields.Integer(
        string="Number of Teams", compute="_compute_team_qty", store=True
    )

    organization_serie_ids = fields.One2many(
        string="Organization Series",
        comodel_name="github.organization.serie",
        inverse_name="organization_id",
    )

    organization_serie_qty = fields.Integer(
        string="Number of Series", store=True, compute="_compute_organization_serie_qty"
    )

    coverage_url_pattern = fields.Char(string="Coverage URL Pattern")

    ci_url_pattern = fields.Char(string="CI URL Pattern")

    analysis_rule_ids = fields.Many2many(
        string="Analysis Rules", comodel_name="github.analysis.rule"
    )

    # Overloadable Section
    @api.model
    def get_conversion_dict(self):
        res = super().get_conversion_dict()
        res.update(
            {
                "name": "name",
                "description": "description",
                "location": "location",
                "email": "email",
                "website_url": "blog",
            }
        )
        return res

    @api.model
    def get_odoo_data_from_github(self, gh_data):
        res = super().get_odoo_data_from_github(gh_data)
        if hasattr(gh_data, "avatar_url"):
            res.update({"image": self.get_base64_image_from_github(gh_data.avatar_url)})
        return res

    def full_update(self):
        self.button_sync_member()
        self.button_sync_repository()
        self.button_sync_team()

    @api.model
    def cron_update_organization_team(self):
        organizations = self.search([])
        organizations.full_update()
        organizations.mapped("team_ids").full_update()
        return True

    # Compute Section
    @api.depends("member_ids", "member_ids.organization_ids")
    def _compute_member_qty(self):
        for organization in self:
            organization.member_qty = len(organization.member_ids)

    @api.depends("repository_ids.organization_id")
    def _compute_repository_qty(self):
        for organization in self:
            organization.repository_qty = len(organization.repository_ids)

    @api.depends("team_ids.organization_id")
    def _compute_team_qty(self):
        for organization in self:
            organization.team_qty = len(organization.team_ids)

    @api.depends("organization_serie_ids.organization_id")
    def _compute_organization_serie_qty(self):
        for organization in self:
            organization.organization_serie_qty = len(
                organization.organization_serie_ids
            )

    def find_related_github_object(self, obj_id=None):
        """Query Github API to find the related object"""
        gh_api = self.get_github_connector()
        return gh_api.get_organization(obj_id or self.github_name)

    # Action section
    def button_sync_member(self):
        gh_org = self.find_related_github_object()
        partner_obj = self.env["res.partner"]
        for organization in self:
            member_ids = []
            for gh_member in gh_org.get_members():
                partner = partner_obj.get_from_id_or_create(gh_data=gh_member)
                member_ids.append(partner.id)
            organization.member_ids = member_ids

    def button_sync_repository(self):
        gh_org = self.find_related_github_object()
        repository_obj = self.env["github.repository"]
        for organization in self:
            repository_ids = []
            for gh_repo in gh_org.get_repos():
                repository = repository_obj.with_context(
                    github_organization_id=organization.id
                ).get_from_id_or_create(gh_data=gh_repo)
                repository_ids.append(repository.id)
            organization.repository_ids = repository_ids

    def button_sync_team(self):
        gh_org = self.find_related_github_object()
        team_obj = self.env["github.team"]
        for organization in self:
            try:
                team_ids = []
                for gh_team in gh_org.get_teams():
                    team = team_obj.get_from_id_or_create(
                        gh_data=gh_team, extra_data={"organization_id": organization.id}
                    )
                    team_ids.append(team.id)
                organization.team_ids = team_ids
            except GithubException as e:
                if e.status == 403:
                    raise exceptions.AccessError(
                        _(
                            "The provided Github Token must have admin read:org"
                            " permissions to the organization '%s'"
                        )
                        % self.name
                    ) from None

    def action_github_repository(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector.action_github_repository"
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_organization_id"] = self.id
        return action

    def action_github_team(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector.action_github_team"
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_organization_id"] = self.id
        return action

    def action_res_partner(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector.action_res_partner"
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_organization_ids"] = self.id
        return action
