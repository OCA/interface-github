# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from subprocess import check_output
from datetime import datetime

from .github import _GITHUB_URL
from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    from git import Repo
except ImportError:
    _logger.debug("Cannot import 'git' python library.")


class GithubRepository(models.Model):
    _name = 'github.repository.branch'
    _inherit = ['abstract.github.model']
    _order = 'repository_id, sequence_serie'

    _github_type = 'repository_branches'
    _github_login_field = False

    _SELECTION_STATE = [
        ('to_download', 'To Download'),
        ('to_analyze', 'To Analyze'),
        ('analyzed', 'Analyzed'),
    ]

    # Column Section
    name = fields.Char(
        string='Name', readonly=True, index=True)

    size = fields.Integer(
        string='Size (Byte) ', readonly=True)

    mb_size = fields.Float(
        string='Size (Megabyte)', store=True, compute='_compute_mb_size')

    complete_name = fields.Char(
        string='Complete Name', store=True, compute='_compute_complete_name')

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository',
        required=True, index=True, readonly=True, ondelete='cascade')

    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        related='repository_id.organization_id', store=True, readonly=True)

    organization_serie_id = fields.Many2one(
        comodel_name='github.organization.serie', string='Organization Serie',
        compute='_compute_organization_serie_id', store=True)

    sequence_serie = fields.Integer(
        string='Sequence Serie', store=True,
        related='organization_serie_id.sequence')

    local_path = fields.Char(
        string='Local Path', compute='_compute_local_path')

    state = fields.Selection(
        string='State', selection=_SELECTION_STATE, default='to_download')

    last_download_date = fields.Datetime(string='Last Download Date')

    last_analyze_date = fields.Datetime(string='Last Analyze Date')

    # Action Section
    @api.multi
    def button_download_code(self):
        return self._download_code()

    @api.multi
    def button_analyze_code(self):
        return self._analyze_code()

    @api.model
    def cron_download_all(self):
        branches = self.search([])
        branches._download_code()
        return True

    @api.model
    def cron_analyze_all(self):
        branches = self.search([('state', '=', 'to_analyze')])
        branches._analyze_code()
        return True

    # Custom
    def create_or_update_from_name(self, repository_id, name):
        branch = self.search([
            ('name', '=', name), ('repository_id', '=', repository_id)])
        if not branch:
            branch = self.create({
                'name': name, 'repository_id': repository_id})
        return branch

    @api.multi
    def _download_code(self):
        for branch in self:
            if not os.path.exists(branch.local_path):
                _logger.info(
                    "Cloning new repository into %s ..." % (branch.local_path))
                # Cloning the repository
                os.makedirs(branch.local_path)

                command = (
                    "cd %s && git clone %s%s/%s.git -b %s .") % (
                        branch.local_path,
                        _GITHUB_URL,
                        branch.repository_id.organization_id.github_login,
                        branch.repository_id.name,
                        branch.name)
                os.system(command)
                branch.write({
                    'last_download_date': datetime.today(),
                    'state': 'to_analyze',
                    })
            else:
                # Update repository
                _logger.info(
                    "Pulling existing repository %s ..." % (branch.local_path))
                try:
                    res = check_output(
                        ['git', 'pull', 'origin', branch.name],
                        cwd=branch.local_path)
                    if branch.state == 'to_download' or\
                            'up-to-date' not in res:
                        branch.write({
                            'last_download_date': datetime.today(),
                            'state': 'to_analyze',
                            })
                    else:
                        branch.write({
                            'last_download_date': datetime.today(),
                            })
                except:
                    # Trying to clean the local folder
                    _logger.warning(
                        "Error when updating the branch %s in the local folder"
                        " %s.\n Deleting the local folder and trying"
                        " again." % (branch.name, branch.local_path))
                    command = ("rm -r %s") % (branch.local_path)
                    os.system(command)
                    branch._download_code()
        return True

    def _get_analyzable_files(self, existing_folder):
        res = []
        for root, dirs, files in os.walk(existing_folder):
            if '/.git' not in root:
                for fic in files:
                    if fic != '.gitignore':
                        res.append(os.path.join(root, fic))
        return res

    @api.model
    def analyze_code_one(self, branch):
        """Overload Me in custom Module that manage Source Code analysis.
        """
        self.ensure_one()
        path = branch.local_path
        # Compute Files Sizes
        size = 0
        for file_path in self._get_analyzable_files(path):
            try:
                size += os.path.getsize(file_path)
            except:
                _logger.warning(
                    "Warning : unable to eval the size of '%s'." % (file_path))

        try:
            repo = Repo(path)
        except:
            # If it's not a correct repository, we flag the branch
            # to be downloaded again
            self.state = 'to_download'
            return {'size': 0}

        # Analyse Commits
        commit_lst = list(repo.iter_commits(branch.name))
        _logger.info(
            "Found %d commits ..." % (len(commit_lst)))

        # here is commits of all branches, to avoid to duplicate commits :
        # all commits done on a 8.0 serie will be present on the 9.0 when the
        # 9.0 serie is created. To avoid that side effect we consider that 9.0
        # commits are only ones that are not present on 8.0 serie.

        # Note : FIXME
        # this algorithm works correctly for version 9.0 and before, but not
        # for the 10.0 version.
        # TODO : investigate.

        # The following lines has been disabled for perfomance reasons.
        # and because it doesn't work for 10.0 version.
        # ignore_branches = self.search([
        #    ('repository_id', '=', branch.repository_id.id),
        #    ('name', '<=', branch.name)])
        # existing_commits = self.env['git.commit'].search([
        #    ('repository_branch_id', 'in', ignore_branches.ids)])
        # existing_names = [x.name for x in existing_commits]
        # new_commits = 0
        # for commit in commit_lst:
        #    if commit.hexsha not in existing_names:
        #        new_commits += 1
        #        self.env['git.commit'].create_or_replace_with_git_data(
        #           commit, branch)
        # _logger.info("%d new commits created." % (new_commits))
        return {'size': size}

    @api.multi
    def _analyze_code(self):
        partial_commit = safe_eval(
            self.env['ir.config_parameter'].get_param(
                'git.partial_commit_during_analyze'))
        for branch in self:
            path = branch.local_path
            if not os.path.exists(path):
                _logger.warning(
                    "Warning Folder %s not found. Analyze skipped." % (path))
            else:
                _logger.info("Analyzing Source Code in %s ..." % (path))
                vals = branch.analyze_code_one(branch)
                vals.update({
                    'last_analyze_date': datetime.today(),
                    'state': 'analyzed',
                })
                # Mark the branch as analyzed
                branch.write(vals)
                if partial_commit:
                    self._cr.commit()
        return True

    # Compute Section
    @api.multi
    @api.depends('name', 'repository_id.name')
    def _compute_complete_name(self):
        for branch in self:
            branch.complete_name =\
                branch.repository_id.name + '/' + branch.name

    @api.multi
    @api.depends('size')
    def _compute_mb_size(self):
        for branch in self:
            branch.mb_size = float(branch.size) / (1024 ** 2)

    @api.multi
    @api.depends('organization_id', 'name')
    def _compute_organization_serie_id(self):
        for branch in self:
            for serie in branch.organization_id.organization_serie_ids:
                if serie.name == branch.name:
                    branch.organization_serie_id = serie

    @api.multi
    @api.depends('complete_name')
    def _compute_local_path(self):
        path = self.env['ir.config_parameter'].get_param(
            'git.source_code_local_path')
        for branch in self:
            branch.local_path = os.path.join(
                path,
                branch.repository_id.organization_id.github_login,
                branch.complete_name)
