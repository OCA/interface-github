# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class GithubOrganization(models.Model):
    _inherit = "github.organization"

    runbot_parse_url = fields.Char(string="URL For Runbot Ids")

    default_author_text = fields.Char()

    runbot_url_pattern = fields.Char(string="Runbot URL Pattern")
