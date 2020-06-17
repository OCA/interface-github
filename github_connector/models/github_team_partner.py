# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


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
