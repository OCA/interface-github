# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class GithubRepository(models.Model):
    _name = 'github.repository'
    _inherit = ['abstract.github.model']
    _order = 'organization_id, name'

    _github_type = 'repository'
    _github_login_field = 'full_name'

    # Column Section
    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        required=True, index=True, readonly=True, ondelete='cascade')

    name = fields.Char(
        string='Name', index=True, required=True, readonly=True)

    complete_name = fields.Char(
        string='Complete Name', readonly=True,
        compute='_compute_complete_name', store=True)

    description = fields.Char(string='Description', readonly=True)

    website = fields.Char(string='Website', readonly=True)

    repository_branch_ids = fields.One2many(
        comodel_name='github.repository.branch',
        inverse_name='repository_id', string='Branches', readonly=True)

    repository_branch_qty = fields.Integer(
        string='Branches Quantity', compute='_compute_repository_branch_qty',
        store=True)

    # Compute Section
    @api.multi
    @api.depends('name', 'organization_id.github_login')
    def _compute_complete_name(self):
        for repository in self:
            repository.complete_name =\
                repository.organization_id.github_login + '/' + repository.name

    @api.multi
    @api.depends('repository_branch_ids.repository_id')
    def _compute_repository_branch_qty(self):
        for repository in self:
            repository.repository_branch_qty =\
                len(repository.repository_branch_ids)

    # Overloadable Section
    @api.model
    def get_odoo_data_from_github(self, data):
        organization_obj = self.env['github.organization']
        res = super(GithubRepository, self).get_odoo_data_from_github(data)
        organization = organization_obj.get_from_id_or_create(data['owner'])
        res.update({
            'name': data['name'],
            'github_url': data['url'],
            'description': data['description'],
            'website': data['homepage'],
            'organization_id': organization.id,
        })
        return res

    @api.multi
    def full_update(self):
        self.button_sync_branch()

    @api.model
    def cron_update_branch_list(self):
        branches = self.search([])
        branches.button_sync_branch()
        return True

    @api.multi
    def button_sync_branch(self):
        github_branch = self.get_github_for('repository_branches')
        branch_obj = self.env['github.repository.branch']
        for repository in self:
            branch_ids = []
            correct_series =\
                repository.organization_id.organization_serie_ids\
                .mapped('name')

            for data in github_branch.list([repository.github_login]):
                # We don't use get_from_id_or_create because repository
                # branches does not have any ids. (very basic object in the
                # Github API)
                if data['name'] in correct_series:
                    branch = branch_obj.create_or_update_from_name(
                        repository.id, data['name'])
                    branch_ids.append(branch.id)
                else:
                    _logger.warning(
                        "the branch '%s'/'%s' has been ignored." % (
                            repository.name, data['name']))
            repository.branch_ids = branch_ids
