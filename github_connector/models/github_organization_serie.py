# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class GithubOrganizationSerie(models.Model):
    _name = 'github.organization.serie'
    _order = 'name'

    # Columns Section
    name = fields.Char(string='Name', required=True)

    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        required=True)
