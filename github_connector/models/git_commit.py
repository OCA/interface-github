# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import models, fields, api


class GitCommit(models.Model):
    _name = 'git.commit'

    # Column Section
    name = fields.Char(
        string='Name', readonly=True, index=True)

    summary = fields.Char(
        string='Summary', readonly=True)

    message = fields.Char(
        string='Message', readonly=True)

    author_id = fields.Many2one(
        string='Git Author', comodel_name='git.author', required=True,
        index=True, ondelete='cascade', readonly=True)

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner',
        related='author_id.partner_id', store=True, readonly=True)

    company_partner_id = fields.Many2one(
        comodel_name='res.partner', string='Company',
        related='author_id.company_partner_id', store=True, readonly=True)

    authored_date = fields.Datetime(
        string='Authored Date', readonly=True)

    repository_branch_id = fields.Many2one(
        string='Repository Branch', comodel_name='github.repository.branch',
        required=True, index=True, ondelete='cascade', readonly=True)

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository',
        related='repository_branch_id.repository_id', store=True,
        readonly=True)

    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        related='repository_id.organization_id', store=True,
        readonly=True)

    organization_serie_id = fields.Many2one(
        comodel_name='github.organization.serie', string='Organization Serie',
        related='repository_branch_id.organization_serie_id', store=True,
        readonly=True)

    insertions_qty = fields.Integer(string='Insertions Qty', readonly=True)
    deletions_qty = fields.Integer(string='Deletions Qty', readonly=True)
    lines_qty = fields.Integer(string='Lines Qty', readonly=True)
    files_qty = fields.Integer(string='Files Qty', readonly=True)

    # Overload Section
    @api.multi
    def unlink(self):
        # Analyzed repository branches should be reanalyzed
        if not self._context.get('dont_change_repository_branch_state', False):
            repository_branch_obj = self.env['github.repository.branch']
            repository_branch_obj.search([
                ('id', 'in', self.mapped('repository_branch_id').ids),
                ('state', '=', 'analyzed')]).write({'state': 'to_analyze'})
        return super(GitCommit, self).unlink()

    # Custom Section
    @api.model
    def create_or_replace_with_git_data(self, myGitCommit, repository_branch):
        git_author_obj = self.env['git.author']
        self.search([('name', '=', myGitCommit.hexsha)]).with_context(
            dont_change_repository_branch_state=True).unlink()
        author = git_author_obj.create_if_not_exist(myGitCommit.author)
        return self.create({
            'name': myGitCommit.hexsha,
            'author_id': author.id,
            'repository_branch_id': repository_branch.id,
            'summary': myGitCommit.summary,
            'message': myGitCommit.message,
            'authored_date': time.strftime(
                "%Y-%m-%d %H:%M",
                time.gmtime(myGitCommit.committed_date)),
            'deletions_qty': myGitCommit.stats.total['deletions'],
            'lines_qty': myGitCommit.stats.total['lines'],
            'insertions_qty': myGitCommit.stats.total['insertions'],
            'files_qty': myGitCommit.stats.total['files'],
        })
