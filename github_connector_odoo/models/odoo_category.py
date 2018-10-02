# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Oscar Alcala (https://twitter.com/oscarolar)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class OdooCategory(models.Model):
    _name = 'odoo.category'

    name = fields.Char()
