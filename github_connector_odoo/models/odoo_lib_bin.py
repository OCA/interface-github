# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class OdooLibBin(models.Model):
    _name = 'odoo.lib.bin'
    _order = 'module_version_qty desc'

    # Column Section
    name = fields.Char(
        string='Name', index=True, required=True, readonly=True)

    module_version_ids = fields.Many2many(
        comodel_name='odoo.module.version', string='Module Versions',
        relation='module_version_lib_bin_rel', column1='lib_bin_id',
        column2='module_version_id', readonly=True)

    module_version_qty = fields.Integer(
        string='Number of Module Versions',
        compute='_compute_module_version_qty', store=True)

    # Compute Section
    @api.multi
    @api.depends('module_version_ids', 'module_version_ids.lib_bin_ids')
    def _compute_module_version_qty(self):
        for lib_bin in self:
            lib_bin.module_version_qty = len(lib_bin.module_version_ids)

    # Custom Section
    @api.model
    def create_if_not_exist(self, name):
        lib_bin = self.search([('name', '=', name)])
        if not lib_bin:
            lib_bin = self.create({'name': name})
        return lib_bin
