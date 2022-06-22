# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# Copyright 2021 Tecnativa - João Marques
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class GithubTeam(models.Model):
    _name = "github.team"
    _inherit = ["abstract.github.model"]
    _order = "name"
    _description = "Github Team"

    _github_login_field = "slug"

    _PRIVACY_SELECTION = [("secret", "Secret"), ("closed", "Closed")]

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

    privacy = fields.Selection(
        selection=_PRIVACY_SELECTION,
        readonly=True,
        default="secret",
        help="The level of privacy this team should have. Can be one of:\n"
        "* secret - only visible to organization owners and members of"
        " this team.\n"
        "* closed - visible to all members of this organization.",
    )

    parent_id = fields.Many2one(
        string="Parent Team", readonly=True, comodel_name="github.team"
    )

    partner_ids = fields.One2many(
        string="Members",
        comodel_name="github.team.partner",
        inverse_name="team_id",
        readonly=True,
    )

    partner_qty = fields.Integer(
        string="Number of Members", compute="_compute_partner_qty", store=True
    )

    repository_ids = fields.One2many(
        string="Repositories",
        comodel_name="github.team.repository",
        inverse_name="team_id",
        readonly=True,
    )

    repository_qty = fields.Integer(
        string="Number of Repositories", compute="_compute_repository_qty", store=True
    )

    description = fields.Char(readonly=True)

    complete_name = fields.Char(
        readonly=True,
        compute="_compute_complete_name",
        store=True,
    )

    github_url = fields.Char(
        string="Github URL", compute="_compute_github_url", readonly=True
    )

    # Compute Section
    @api.depends("github_name", "organization_id.github_name")
    def _compute_github_url(self):
        for team in self:
            team.github_url = (
                "https://github.com/orgs/{organization_name}/"
                "teams/{team_name}".format(
                    organization_name=team.organization_id.github_name,
                    team_name=team.github_name,
                )
            )

    @api.depends("name", "organization_id.github_name")
    def _compute_complete_name(self):
        for team in self:
            team.complete_name = "{}/{}".format(
                team.organization_id.github_name, team.github_name
            )

    @api.depends("partner_ids")
    def _compute_partner_qty(self):
        for team in self:
            team.partner_qty = len(team.partner_ids)

    @api.depends("repository_ids")
    def _compute_repository_qty(self):
        for team in self:
            team.repository_qty = len(team.repository_ids)

    # Overloadable Section
    @api.model
    def get_conversion_dict(self):
        res = super().get_conversion_dict()
        res.update({"name": "name", "description": "description", "privacy": "privacy"})
        return res

    @api.model
    def get_odoo_data_from_github(self, gh_data):
        organization_obj = self.env["github.organization"]
        res = super().get_odoo_data_from_github(gh_data)
        if gh_data.organization:
            organization_id = organization_obj.get_from_id_or_create(
                gh_data=gh_data.organization
            ).id
        else:
            organization_id = False
        res.update({"organization_id": organization_id})
        return res

    def get_github_base_obj_for_creation(self):
        self.ensure_one()
        gh_api = self.get_github_connector()
        return gh_api.get_organization(self.organization_id.github_name)

    def create_in_github(self):
        """Create an object in Github through the API"""
        self.ensure_one()
        # Create in Github
        gh_base_obj = self.get_github_base_obj_for_creation()
        gh_team = gh_base_obj.create_team(
            name=self.name, description=self.description or "", privacy=self.privacy
        )
        # Create in Odoo with the returned data and update object
        data = self.get_odoo_data_from_github(gh_team)
        new_item = self._create_from_github_data(data)
        new_item.full_update()
        new_item._hook_after_github_creation()
        return new_item

    def full_update(self):
        self.button_sync_member()
        self.button_sync_repository()

    def find_related_github_object(self, obj_id=None):
        """Query Github API to find the related object"""
        self.get_github_connector()
        return self.organization_id.find_related_github_object().get_team(
            int(obj_id or self.github_id_external)
        )

    # Action Section
    def button_sync_member(self):
        partner_obj = self.env["res.partner"]
        gh_team = self.find_related_github_object()
        for team in self:
            partner_data = []
            # Fetching the role after getting each user requires more API calls for
            # each user, so we fetch the users in 2 steps, one for each role
            for gh_user in gh_team.get_members(role="member"):
                partner = partner_obj.get_from_id_or_create(gh_data=gh_user)
                partner_data.append({"partner_id": partner.id, "role": "member"})
            for gh_user in gh_team.get_members(role="maintainer"):
                partner = partner_obj.get_from_id_or_create(gh_data=gh_user)
                partner_data.append({"partner_id": partner.id, "role": "maintainer"})
            team.partner_ids = [(2, x.id, False) for x in team.partner_ids]
            team.partner_ids = [(0, False, x) for x in partner_data]

    def button_sync_repository(self):
        repository_obj = self.env["github.repository"]
        gh_team = self.find_related_github_object()
        for team in self:
            repository_data = []
            for gh_repo in gh_team.get_repos():
                repository = repository_obj.get_from_id_or_create(gh_data=gh_repo)
                if gh_repo.permissions.admin:
                    permission = "admin"
                elif gh_repo.permissions.push:
                    permission = "write"
                else:
                    permission = "read"
                repository_data.append(
                    {"repository_id": repository.id, "permission": permission}
                )
            team.repository_ids = [(2, x.id, False) for x in team.repository_ids]
            team.repository_ids = [(0, False, x) for x in repository_data]

    def action_github_team_partner_from_team(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector.action_github_team_partner_from_team"
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_team_id"] = self.id
        return action

    def action_github_team_repository_from_team(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector.action_github_team_repository_from_team"
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_team_id"] = self.id
        return action
