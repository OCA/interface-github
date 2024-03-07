# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# Copyright 2021 Tecnativa - João Marques
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# pylint: disable=missing-manifest-dependency
from github.GithubException import UnknownObjectException

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "abstract.github.model"]

    _github_login_field = "login"
    _need_individual_call = True
    _field_list_prevent_overwrite = ["name", "website", "email", "image_1920"]

    # Column Section
    is_bot_account = fields.Boolean(
        string="Is Bot Github Account",
        help="Check this box if this " "account is a bot or similar.",
    )

    github_team_partner_ids = fields.One2many(
        string="Teams",
        comodel_name="github.team.partner",
        inverse_name="partner_id",
        readonly=True,
    )

    github_team_qty = fields.Integer(
        string="Number of Teams", compute="_compute_github_team_qty", store=True
    )

    organization_ids = fields.Many2many(
        string="Organizations",
        comodel_name="github.organization",
        relation="github_organization_partner_rel",
        column1="partner_id",
        column2="organization_id",
        readonly=True,
    )

    organization_qty = fields.Integer(
        string="Number of Organizations",
        compute="_compute_organization_qty",
        store=True,
    )

    # Constraints Section
    _sql_constraints = [
        (
            "github_login_uniq",
            "unique(github_name)",
            "Two different partners cannot have the same Github Login",
        )
    ]

    @api.constrains("github_name", "is_company")
    def _check_login_company(self):
        for partner in self:
            if partner.is_company and partner.github_name:
                raise UserError(
                    _("A company ('%s') can not have a Github login" " associated.")
                    % partner.name
                )

    # Compute Section
    @api.depends("organization_ids", "organization_ids.member_ids")
    def _compute_organization_qty(self):
        for partner in self:
            partner.organization_qty = len(partner.organization_ids)

    @api.depends("github_team_partner_ids")
    def _compute_github_team_qty(self):
        data = self.env["github.team.partner"].read_group(
            [("partner_id", "in", self.ids)], ["partner_id"], ["partner_id"]
        )
        mapping = {data["partner_id"][0]: data["partner_id_count"] for data in data}
        for item in self:
            item.github_team_qty = mapping.get(item.id, 0)

    # Custom Section
    @api.model
    def get_conversion_dict(self):
        res = super().get_conversion_dict()
        res.update({"website": "blog", "email": "email"})
        return res

    @api.model
    def get_odoo_data_from_github(self, gh_data):
        res = super().get_odoo_data_from_github(gh_data)
        res.update({"name": gh_data.name or "%s (Github)" % gh_data.login})
        if hasattr(gh_data, "avatar_url"):
            res.update(
                {"image_1920": self.get_base64_image_from_github(gh_data.avatar_url)}
            )
        return res

    def find_related_github_object(self, obj_id=None):
        """Query Github API to find the related object"""
        gh_api = self.get_github_connector()
        try:
            return gh_api.get_user_by_id(int(obj_id or self.github_id_external))
        except UnknownObjectException:
            return gh_api.get_user(self.github_name)

    def action_github_organization(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector.action_github_organization"
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_member_ids"] = self.id
        return action

    def action_github_team_partner_from_partner(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector.action_github_team_partner_from_partner"
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_partner_id"] = self.id
        return action
