# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class GithubTeamPartner(models.Model):
    _name = "github.team.partner"
    _description = "Github Team Partner"
    _order = "team_id, partner_id"

    _ROLE_SELECTION = [("member", "Member"), ("maintainer", "Maintainer")]

    # Column Section
    team_id = fields.Many2one(
        comodel_name="github.team",
        string="Team",
        required=True,
        index=True,
        readonly=True,
        ondelete="cascade",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Member",
        required=True,
        index=True,
        readonly=True,
        ondelete="cascade",
    )

    role = fields.Selection(
        selection=_ROLE_SELECTION, string="Role", required=True, readonly=True
    )

    context_search_default_team_id = fields.Integer(
        compute="_compute_context_search_default"
    )
    context_search_default_partner_id = fields.Integer(
        compute="_compute_context_search_default"
    )

    @api.depends_context("search_default_team_id", "search_default_partner_id")
    def _compute_context_search_default(self):
        """Compute the context value for the search terms
        into helper fields for the view
        """
        for record in self:
            record.context_search_default_team_id = self.env.context.get(
                "search_default_team_id", False
            )
            record.context_search_default_partner_id = self.env.context.get(
                "search_default_partner_id", False
            )
