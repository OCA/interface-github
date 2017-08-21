# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class OdooLibPython(models.Model):
    _name = 'odoo.lib.python'
    _order = 'module_version_qty desc'

    # Column Section
    name = fields.Char(
        string='Name', index=True, required=True, readonly=True)

    module_version_ids = fields.Many2many(
        comodel_name='odoo.module.version', string='Module Versions',
        relation='module_version_lib_python_rel', column1='lib_python_id',
        column2='module_version_id', readonly=True)

    module_version_qty = fields.Integer(
        string='Number of Module Versions',
        compute='_compute_module_version_qty', store=True)

    # Compute Section
    @api.multi
    @api.depends('module_version_ids', 'module_version_ids.lib_python_ids')
    def _compute_module_version_qty(self):
        for lib_python in self:
            lib_python.module_version_qty = len(lib_python.module_version_ids)

    # Custom Section
    @api.model
    def create_if_not_exist(self, name):
        lib_python = self.search([('name', '=', name)])
        if not lib_python:
            lib_python = self.create({'name': name})
        return lib_python
