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

    _PRIVACY_SELECTION = [
        ('secret', 'Secret'),
        ('closed', 'Closed'),
    ]

    # Column Section
    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        required=True, index=True, readonly=True, ondelete='cascade')

    name = fields.Char(
        string='Name', index=True, required=True, readonly=True)

    privacy = fields.Selection(
        string='Privacy', selection=_PRIVACY_SELECTION, readonly=True,
        default='secret',
        help="The level of privacy this team should have. Can be one of:\n"
        "* secret - only visible to organization owners and members of"
        " this team.\n"
        "* closed - visible to all members of this organization.")

    parent_id = fields.Many2one(
        string='Parent Team', readonly=True, comodel_name='github.team')

    partner_ids = fields.One2many(
        string='Members', comodel_name='github.team.partner',
        inverse_name='team_id', readonly=True)

    partner_qty = fields.Integer(
        string='Members Quantity', compute='_compute_partner_qty',
        store=True)

    repository_ids = fields.One2many(
        string='Repositories', comodel_name='github.team.repository',
        inverse_name='team_id', readonly=True)

    repository_qty = fields.Integer(
        string='Repositories Quantity', compute='_compute_repository_qty',
        store=True)

    description = fields.Char(string='Description', readonly=True)

    complete_name = fields.Char(
        string='Complete Name', readonly=True,
        compute='_compute_complete_name', store=True)

    github_url = fields.Char(
        string='Github URL', compute='_compute_github_url', readonly=True)

    # Compute Section
    @api.multi
    @api.depends('github_login', 'organization_id.github_login')
    def _compute_github_url(self):
        for team in self:
            team.github_url = "https://github.com/orgs/{organization_name}/"\
                "teams/{team_name}".format(
                    organization_name=team.organization_id.github_login,
                    team_name=team.github_login)

    @api.multi
    @api.depends('name', 'organization_id.github_login')
    def _compute_complete_name(self):
        for team in self:
            team.complete_name =\
                team.organization_id.github_login + '/'\
                + (team.github_login and team.github_login or '')

    @api.multi
    @api.depends('partner_ids')
    def _compute_partner_qty(self):
        for team in self:
            team.partner_qty = len(team.partner_ids)

    @api.multi
    @api.depends('repository_ids')
    def _compute_repository_qty(self):
        for team in self:
            team.repository_qty = len(team.repository_ids)

    # Overloadable Section
    def get_odoo_data_from_github(self, data):
        organization_obj = self.env['github.organization']
        res = super(GithubTeam, self).get_odoo_data_from_github(data)
        organization = organization_obj.get_from_id_or_create(
            data['organization'])
        res.update({
            'name': data['name'],
            'description': data['description'],
            'privacy': data['privacy'],
            'organization_id': organization.id,
        })
        return res

    @api.multi
    def get_github_data_from_odoo(self):
        self.ensure_one()
        return {
            'name': self.name,
            'description': self.description and self.description or '',
            'privacy': self.privacy,
        }

    @api.multi
    def get_github_args_for_creation(self):
        self.ensure_one()
        return [
            self.organization_id.github_login,
        ]

    @api.multi
    def full_update(self):
        self.button_sync_member()
        self.button_sync_repository()

    # Action Section
    @api.multi
    def button_sync_member(self):
        partner_obj = self.env['res.partner']
        connector_member = self.get_github_connector(
            'team_members_member')
        connector_maintainer = self.get_github_connector(
            'team_members_maintainer')
        for team in self:
            partner_data = []
            for data in connector_member.list([team.github_id_external]):
                partner = partner_obj.get_from_id_or_create(data)
                partner_data.append({
                    'partner_id': partner.id, 'role': 'member'})
            for data in connector_maintainer.list([team.github_id_external]):
                partner = partner_obj.get_from_id_or_create(data)
                partner_data.append({
                    'partner_id': partner.id, 'role': 'maintainer'})
            team.partner_ids = [
                (2, x.id, False) for x in team.partner_ids]
            team.partner_ids = [(0, False, x) for x in partner_data]

    @api.multi
    def button_sync_repository(self):
        repository_obj = self.env['github.repository']
        connector = self.get_github_connector('team_repositories')
        for team in self:
            repository_data = []
            for data in connector.list([team.github_id_external]):
                repository = repository_obj.get_from_id_or_create(data)
                if data['permissions']['admin'] is True:
                    permission = 'admin'
                elif data['permissions']['push'] is True:
                    permission = 'write'
                else:
                    permission = 'read'
                repository_data.append({
                    'repository_id': repository.id, 'permission': permission})

            team.repository_ids = [
                (2, x.id, False) for x in team.repository_ids]
            team.repository_ids = [(0, False, x) for x in repository_data]
