# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    author_ids = fields.One2many(
        comodel_name='odoo.author', string='Authors',
        inverse_name='partner_id', readonly=True
    )
