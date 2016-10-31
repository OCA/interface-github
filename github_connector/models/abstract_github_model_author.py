# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AbtractGithubModelAuthor(models.AbstractModel):
    """
    This Abstract Model is used to share behaviour between some github models
    that have an author_id.
    * define the company related to the author.
    """

    _name = 'abstract.github.model.author'
    _inherit = ['abstract.github.model']

    author_id = fields.Many2one(
        comodel_name='res.partner', string='Author', readonly=True,
        required=True)

    company_author_id = fields.Many2one(
        comodel_name='res.partner', string='Author Company')

    # Overloadable Section
    def get_odoo_data_from_github(self, data):
        partner_obj = self.env['res.partner']
        res = super(AbtractGithubModelAuthor, self)\
            .get_odoo_data_from_github(data)
        partner = partner_obj.get_from_id_or_create(data['user'])
        res.update({
            'author_id': partner.id,
        })
        return res

    @api.model
    def create(self, vals):
        # Set related company of the author, if defined
        partner = self.env['res.partner'].browse(vals.get('author_id'))
        vals.update({'company_author_id': partner.parent_id.id})
        res = super(AbtractGithubModelAuthor, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('author_id'):
            # Set related company of the author, if defined
            partner = self.env['res.partner'].browse(vals.get('author_id'))
            if partner.company_id:
                vals.update({'company_author_id': partner.company_id.id})
        res = super(AbtractGithubModelAuthor, self).write(vals)
        return res
