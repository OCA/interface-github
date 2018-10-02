# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class OdooMaintainer(models.Model):
    _name = 'odoo.maintainer'
    _order = 'module_qty desc, name'

    # Column Section
    name = fields.Char(
        string='Name', store=True, readonly=True, index=True)

    module_version_ids = fields.Many2many(
        string='Module Versions', comodel_name='odoo.module.version',
        relation='github_module_version_maintainer_rel',
        column1='maintainer_id', column2='module_version_id', readonly=True)

    module_ids = fields.Many2many(
        string='Modules', comodel_name='odoo.module',
        relation='github_module_maintainer_rel',
        column1='maintainer_id', column2='module_id', readonly=True)

    module_qty = fields.Integer(
        string='Number of Modules',
        compute='_compute_module_qty', store=True)

    @api.multi
    @api.depends('module_ids.maintainer_ids')
    def _compute_module_qty(self):
        for maintainer in self:
            maintainer.module_qty = len(maintainer.module_ids)

    # Custom Section
    @api.model
    def create_if_not_exist(self, name):
        maintainer = self.search([('name', '=', name)])
        if not maintainer:
            maintainer = self.create({'name': name})
        return maintainer
