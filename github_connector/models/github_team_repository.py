# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class GithubTeamRepository(models.Model):
    _name = "github.team.repository"
    _description = "Github Team Repository"
    _order = "team_id, repository_id"

    _PERMISSION_SELECTION = [
        ("undefined", "Undefined"),
        ("read", "Read"),
        ("write", "Write"),
        ("admin", "Admin"),
    ]

    # Column Section
    team_id = fields.Many2one(
        comodel_name="github.team",
        string="Team",
        required=True,
        index=True,
        readonly=True,
        ondelete="cascade",
    )

    repository_id = fields.Many2one(
        comodel_name="github.repository",
        string="Repository",
        required=True,
        index=True,
        readonly=True,
        ondelete="cascade",
    )

    permission = fields.Selection(
        selection=_PERMISSION_SELECTION,
        required=True,
        readonly=True,
    )

    context_search_default_team_id = fields.Integer(
        compute="_compute_context_search_default"
    )
    context_search_default_repository_id = fields.Integer(
        compute="_compute_context_search_default"
    )

    @api.depends_context("search_default_team_id", "search_default_repository_id")
    def _compute_context_search_default(self):
        """Compute the context value for the search terms
        into helper fields for the view
        """
        for record in self:
            record.context_search_default_team_id = self.env.context.get(
                "search_default_team_id", False
            )
            record.context_search_default_repository_id = self.env.context.get(
                "search_default_repository_id", False
            )
