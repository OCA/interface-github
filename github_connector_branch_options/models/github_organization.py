# Copyright Cetmix OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class GithubOrganization(models.Model):
    _inherit = "github.organization"

    create_series = fields.Boolean(
        string="Auto Create Series",
        help="If checked, during synchronization for branches"
        " for which no series have been created,"
        "they will be created automatically.",
    )
