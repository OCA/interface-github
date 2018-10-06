# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class GithubSerie(models.Model):
    _inherit = 'github.serie'

    type = fields.Selection(selection_add=[('odoo', 'Odoo')])
