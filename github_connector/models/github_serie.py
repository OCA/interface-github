# Copyright (C) 2018-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class GithubSerie(models.Model):
    _name = 'github.serie'
    _order = 'sequence, name'

    # Columns Section
    name = fields.Char(string='Name', required=True)

    sequence = fields.Integer(string='Sequence', required=True)

    type = fields.Selection(
        selection=[('normal', 'Normal')], required=True, default='normal')
