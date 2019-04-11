# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class OdooLicense(models.Model):
    _name = 'odoo.license'
    _description = 'Odoo License'
    _order = 'name'

    # Column Section
    name = fields.Char(
        string='Name', index=True, required=True, readonly=True)

    module_version_ids = fields.One2many(
        comodel_name='odoo.module.version', inverse_name='license_id',
        string='Module Versions')

    module_version_qty = fields.Integer(
        string='Number of Module Versions',
        compute='_compute_module_version_qty', store=True)

    website = fields.Char(string='Website')

    image = fields.Binary(string='Icon Image')

    description = fields.Text(string='Description')

    active = fields.Boolean(string='Active', default=True)

    # Constrains Section
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists !"),
    ]

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
