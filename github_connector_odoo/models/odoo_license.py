# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class OdooLicense(models.Model):
    _name = 'odoo.license'
    _order = 'module_version_qty desc, name'

    # Column Section
    name = fields.Char(
        string='Name', index=True, required=True, readonly=True)

    module_version_ids = fields.One2many(
        comodel_name='odoo.module.version', inverse_name='license_id',
        string='Module Versions')

    module_version_qty = fields.Integer(
        string='Module Versions Quantity',
        compute='_compute_module_version_qty', store=True)

    # Compute Section
    @api.multi
    @api.depends('module_version_ids.license_id')
    def _compute_module_version_qty(self):
        for module in self:
            module.module_version_qty = len(module.module_version_ids)

    # Custom Section
    @api.model
    def create_if_not_exist(self, name):
        module = self.search([('name', '=', name)])
        if not module:
            module = self.create({'name': name})
        return module
