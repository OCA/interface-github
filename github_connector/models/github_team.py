# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class GithubTeam(models.Model):
    _name = 'github.team'
    _inherit = ['abstract.github.model']
    _order = 'name'

    _github_type = 'team'
    _github_login_field = 'slug'

    # Column Section
    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        required=True, select=True, readonly=True, ondelete='cascade')

    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    member_ids = fields.Many2many(
        string='Members', comodel_name='res.partner',
        relation='github_team_partner_rel', column1='team_id',
        column2='partner_id', readonly=True)

    member_qty = fields.Integer(
        string='Members Quantity', compute='_compute_member_qty', store=True)

    description = fields.Char(string='Description', readonly=True)

    # Compute Section
    @api.multi
    @api.depends('member_ids', 'member_ids.team_ids')
    def _compute_member_qty(self):
        for team in self:
            team.member_qty = len(team.member_ids)

    # Overloadable Section
    def get_odoo_data_from_github(self, data):
        res = super(GithubTeam, self).get_odoo_data_from_github(data)
        res.update({
            'name': data['name'],
            'description': data['description'],
        })
        return res

    @api.multi
    def full_update(self):
        self.button_sync_member()

    # Action Section
    @api.multi
    def button_sync_member(self):
        partner_obj = self.env['res.partner']
        github_member = self.get_github_for('team_members')
        for team in self:
            member_ids = []
            for data in github_member.list([team.github_id]):
                partner = partner_obj.get_from_id_or_create(data)
                member_ids.append(partner.id)
            team.member_ids = member_ids
