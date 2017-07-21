# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields
from openerp.tools.translate import _


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'abstract.github.model']

    _github_type = 'user'
    _github_login_field = 'login'
    _need_individual_call = True

    # Column Section
    is_bot_account = fields.Boolean(
        string='Is Bot Github Account', help="Check this box if this"
        "account is a bot, or something similar.")

    team_ids = fields.Many2many(
        string='Teams', comodel_name='github.team',
        relation='github_team_partner_rel', column1='partner_id',
        column2='team_id', readonly=True)

    team_qty = fields.Integer(
        string='Teams Quantity', compute='_compute_team_qty', store=True)

    organization_ids = fields.Many2many(
        string='Organizations', comodel_name='github.organization',
        relation='github_organization_partner_rel', column1='partner_id',
        column2='organization_id', readonly=True)

    organization_qty = fields.Integer(
        string='Organizations Quantity', compute='_compute_organization_qty',
        store=True)

    # Compute Section
    @api.multi
    @api.depends('organization_ids', 'organization_ids.member_ids')
    def _compute_organization_qty(self):
        for partner in self:
            partner.organization_qty = len(partner.organization_ids)

    # Constraints Section
    _sql_constraints = [
        (
            'github_login_uniq', 'unique(github_login)',
            "Two partners with the same Github Login ?"
            " Dude, it is impossible !")
    ]

    @api.multi
    @api.constrains('github_login', 'is_company')
    def _check_login_company(self):
        for partner in self:
            if partner.is_company and partner.github_login:
                raise Warning(_(
                    "The company '%s' can not have a github login.") % (
                    partner.name))

    # Compute Section
    @api.multi
    @api.depends('team_ids', 'team_ids.member_ids')
    def _compute_team_qty(self):
        for partner in self:
            partner.team_qty = len(partner.team_ids)

    # Custom Section
    @api.model
    def get_odoo_data_from_github(self, data):
        res = super(ResPartner, self).get_odoo_data_from_github(data)
        res.update({
            'name':
            data['name'] and data['name'] or
            '%s (Github)' % data['login'],
            'website': data['blog'],
            'email': data['email'],
            'image': self.get_base64_image_from_github(data['avatar_url']),
        })
        return res
