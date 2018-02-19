# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Migrated to version 11.0: Petar Najman (petar.najman@modoolar.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields


class GithubOrganization(models.Model):
    _inherit = 'github.organization'

    runbot_parse_url = fields.Char(
        string='URL For Runbot Ids', oldname='runbot_url')

    default_author_text = fields.Char(string='Default Author Text')

    runbot_url_pattern = fields.Char(string='Runbot URL Pattern')
