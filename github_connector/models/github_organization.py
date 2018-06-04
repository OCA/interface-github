# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class GithubOrganization(models.Model):
    _name = 'github.organization'
    _inherit = ['abstract.github.model']
    _order = 'name'

    _github_type = 'organization'
    _github_login_field = 'login'

    # Columns Section
    name = fields.Char(
        string='Organization Name', required=True, readonly=True)

    image = fields.Binary(string='Image', readonly=True)

    description = fields.Char(string='Description', readonly=True)

    email = fields.Char(string='Email', readonly=True)

    website_url = fields.Char(string='Website URL', readonly=True)

    location = fields.Char(string='Location', readonly=True)

    ignored_repository_names = fields.Text(
        string='Ignored Repositories', help="Set here repository names"
        " you want to ignore. One repository per line."
        " If set, the repositories will be created, but branches"
        " synchronization and source code download will be disabled."
        " Exemple:\n"
        "purchase-workflow\nOCB\nOpenUpgrade\n")

    member_ids = fields.Many2many(
        string='Members', comodel_name='res.partner',
        relation='github_organization_partner_rel', column1='organization_id',
        column2='partner_id', readonly=True)

    member_qty = fields.Integer(
        string='Number of Members', compute='_compute_member_qty',
        store=True)

    repository_ids = fields.One2many(
        string='Repositories', comodel_name='github.repository',
        ondelete='cascade', inverse_name='organization_id', readonly=True)

    repository_qty = fields.Integer(
        string='Number of Repositories', compute='_compute_repository_qty',
        store=True)

    team_ids = fields.One2many(
        string='Teams', comodel_name='github.team',
        inverse_name='organization_id', readonly=True)

    team_qty = fields.Integer(
        string='Number of Teams', compute='_compute_team_qty',
        store=True)

    organization_serie_ids = fields.One2many(
        string='Organization Series',
        comodel_name='github.organization.serie',
        inverse_name='organization_id')

    organization_serie_qty = fields.Integer(
        string='Number of Series', store=True,
        compute='_compute_organization_serie_qty')

    coverage_url_pattern = fields.Char(string='Coverage URL Pattern')

    ci_url_pattern = fields.Char(string='CI URL Pattern')

    # Overloadable Section
    @api.model
    def get_odoo_data_from_github(self, data):
        res = super(GithubOrganization, self).get_odoo_data_from_github(data)
        keys = ['name', 'description', 'location', 'blog', 'email']
        for key in keys:
            if key in data:
                res.update({key: data[key]})
        if 'avatar_url' in data:
            res.update({
                'image': self.get_base64_image_from_github(data['avatar_url']),
            })
        return res

    @api.multi
    def full_update(self):
        self.button_sync_member()
        self.button_sync_repository()
        self.button_sync_team()

    @api.model
    def cron_update_organization_team(self):
        organizations = self.search([])
        organizations.full_update()
        organizations.mapped('team_ids').full_update()
        return True

    # Compute Section
    @api.multi
    @api.depends('member_ids', 'member_ids.organization_ids')
    def _compute_member_qty(self):
        for organization in self:
            organization.member_qty = len(organization.member_ids)

    @api.multi
    @api.depends('repository_ids.organization_id')
    def _compute_repository_qty(self):
        for organization in self:
            organization.repository_qty = len(organization.repository_ids)

    @api.multi
    @api.depends('team_ids.organization_id')
    def _compute_team_qty(self):
        for organization in self:
            organization.team_qty = len(organization.team_ids)

    @api.multi
    @api.depends('organization_serie_ids.organization_id')
    def _compute_organization_serie_qty(self):
        for organization in self:
            organization.organization_serie_qty =\
                len(organization.organization_serie_ids)

    # Action section
    @api.multi
    def button_sync_member(self):
        github_member = self.get_github_connector('organization_members')
        partner_obj = self.env['res.partner']
        for organization in self:
            member_ids = []
            for data in github_member.list([organization.github_login]):
                partner = partner_obj.get_from_id_or_create(data)
                member_ids.append(partner.id)
            organization.member_ids = member_ids

    @api.multi
    def button_sync_repository(self):
        repository_obj = self.env['github.repository']
        github_repo = self.get_github_connector('organization_repositories')
        for organization in self:
            repository_ids = []
            for data in github_repo.list([organization.github_login]):
                repository = repository_obj.get_from_id_or_create(data)
                repository_ids.append(repository.id)
            organization.repository_ids = repository_ids

    @api.multi
    def button_sync_team(self):
        team_obj = self.env['github.team']
        github_team = self.get_github_connector('organization_teams')
        for organization in self:
            team_ids = []
            for data in github_team.list([organization.github_login]):
                team = team_obj.get_from_id_or_create(
                    data, {'organization_id': organization.id})
                team_ids.append(team.id)
            organization.team_ids = team_ids
