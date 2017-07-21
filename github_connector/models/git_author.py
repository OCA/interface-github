# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class GitAuthor(models.Model):
    _name = 'git.author'
    _order = 'commit_qty desc'

    # Column Section
    name = fields.Char(
        string='Name', store=True, index=True, readonly=True)

    email = fields.Char(
        string='Email', store=True, readonly=True, index=True)

    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner')

    company_partner_id = fields.Many2one(
        string='Company', comodel_name='res.partner',
        domain="[('is_company', '=', True)]")

    commit_ids = fields.One2many(
        comodel_name='git.commit', inverse_name='author_id',
        string='Commits')

    commit_qty = fields.Integer(
        string='Commits Quantity', compute='_compute_commit_qty', store=True)

    # Compute Section
    @api.multi
    @api.depends('commit_ids.author_id')
    def _compute_commit_qty(self):
        for author in self:
            author.commit_qty = len(author.commit_ids)

    # Custom Section
    @api.model
    def create_if_not_exist(self, myGitAuthor):
        partner_obj = self.env['res.partner']
        author = self.search([('email', '=', myGitAuthor.email)])
        if not author:
            # Try to guess partner_id, by email
            partner = partner_obj.search([
                ('email', '=', myGitAuthor.email)], limit=1)
            partner_id = len(partner) and partner[0].id or False
            author = self.create({
                'name': myGitAuthor.name,
                'email': myGitAuthor.email,
                'partner_id': partner_id,
            })
        return author
