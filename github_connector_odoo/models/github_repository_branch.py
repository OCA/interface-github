# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from os.path import join as opj

from openerp import models, fields, api

from openerp.modules import load_information_from_description_file

# Hard define this value to make this module working with or without
# the patch (that backports V10 manifests analysis code.
MANIFEST_NAMES = ('__manifest__.py', '__openerp__.py')

_logger = logging.getLogger(__name__)


class GithubRepositoryBranch(models.Model):
    _inherit = ['github.repository.branch']

    module_paths = fields.Text(
        string='Module Paths', help="Set here extra relative paths"
        " you want to scan to find modules. If not set, root path will be"
        " scanned. One repository per line. Exemple:\n"
        "./addons/\n"
        "./openerp/addons/")

    module_version_ids = fields.One2many(
        comodel_name='odoo.module.version',
        inverse_name='repository_branch_id', string='Module Versions')

    module_version_qty = fields.Integer(
        string='Module Versions Quantity',
        compute='_compute_module_version_qty')

    coverage_url = fields.Char(
        string='Coverage Url', store=True, multi='complete_name',
        compute='_compute_multi_from_complete_name')

    coverage_image_url = fields.Char(
        string='Coverage Image Url', store=True, multi='complete_name',
        compute='_compute_multi_from_complete_name')

    integration_service_url = fields.Char(
        string='Integration Service Url', store=True, multi='complete_name',
        compute='_compute_multi_from_complete_name')

    integration_service_image_url = fields.Char(
        string='Integration Service Image Url', store=True,
        multi='complete_name',
        compute='_compute_multi_from_complete_name')

    runbot_url = fields.Char(
        string='Runbot Url', multi='complete_name',
        compute='_compute_multi_from_complete_name')

    runbot_image_url = fields.Char(
        string='Runbot Image Url',
        multi='complete_name',
        compute='_compute_multi_from_complete_name')

    github_url = fields.Char(
        string='Github Url', store=True,
        multi='complete_name',
        compute='_compute_multi_from_complete_name')

    # Compute Section
    @api.multi
    @api.depends('name', 'repository_id.complete_name', 'repository_id.ci_id')
    def _compute_multi_from_complete_name(self):
        for branch in self:
            # Compute Coverage Service Url and Image Url
            branch.coverage_url =\
                'https://coveralls.io/github/' +\
                branch.repository_id.complete_name +\
                '?branch=' + branch.name
            branch.coverage_image_url =\
                'https://coveralls.io/repos/github/' +\
                branch.repository_id.complete_name +\
                '/badge.svg?branch=' + branch.name

            # Compute Integration Service Url and Image Url
            branch.integration_service_url =\
                'https://travis-ci.org/' +\
                branch.repository_id.complete_name
            branch.integration_service_image_url =\
                'https://travis-ci.org/' +\
                branch.repository_id.complete_name +\
                '.svg?branch=' + branch.name

            # Compute Github Url
            branch.github_url =\
                'https://github.com/' +\
                branch.repository_id.complete_name +\
                '/tree/' + branch.name

            # Compute Runbot Service Url and Image Url
            branch.runbot_url =\
                'https://runbot.odoo-community.org/runbot/' +\
                str(branch.repository_id.ci_id) + '/' +\
                branch.name
            branch.runbot_image_url =\
                'https://runbot.odoo-community.org/runbot/badge/flat/' +\
                str(branch.repository_id.ci_id) + '/' +\
                branch.name + '.svg'

    @api.multi
    @api.depends(
        'module_version_ids', 'module_version_ids.repository_branch_id')
    def _compute_module_version_qty(self):
        for repository_branch in self:
            repository_branch.module_version_qty =\
                len(repository_branch.module_version_ids)

    # Custom Section
    @api.model
    def _set_state_to_analyse(self):
        """ function called when the module is installed to set all branches
        to analyze again.
        """
        branches = self.search([('state', '=', 'analyzed')])
        branches.write({'state': 'to_analyze'})

    @api.model
    def analyze_code_one(self, branch):
        # Change log level to avoid warning, when parsing odoo manifests
        logger1 = logging.getLogger('openerp.modules.module')
        logger2 = logging.getLogger('openerp.addons.base.module.module')
        currentLevel1 = logger1.level
        currentLevel2 = logger2.level
        logger1.setLevel(logging.ERROR)
        logger2.setLevel(logging.ERROR)

        try:
            module_version_obj = self.env['odoo.module.version']
            # Delete all associated module versions
            module_versions = module_version_obj.search([
                ('repository_branch_id', '=', branch.id)])
            module_versions.with_context(
                dont_change_repository_branch_state=True).unlink()

            # Compute path(s) to analyze
            if branch.module_paths:
                paths = []
                for path in branch.module_paths.split('\n'):
                    if path.strip():
                        paths.append(branch.local_path + '/' + path)
            else:
                paths = [branch.local_path]

            # Scan each path, if exists
            for path in paths:
                if not os.path.exists(path):
                    _logger.warning(
                        "Unable to analyse %s. Source code not found." % (
                            path))
                else:
                    # Analyze folders and create module versions
                    _logger.info("Analyzing repository %s ..." % (path))
                    for module_name in self.listdir(path):
                        module_info = load_information_from_description_file(
                            module_name, path + '/' + module_name)

                        # Create module version, if the module is installable
                        # in the serie
                        if module_info.get('installable', False):
                            module_info['technical_name'] = module_name
                            module_version_obj.create_or_update_from_manifest(
                                module_info, branch)
        finally:
            # Reset Original level for module logger
            logger1.setLevel(currentLevel1)
            logger2.setLevel(currentLevel2)
        return super(GithubRepositoryBranch, self).analyze_code_one(branch)

    # Copy Paste from Odoo Core
    # This function is for the time being in another function.
    # (Ref: openerp/modules/module.py)
    def listdir(self, dir):
        def clean(name):
            name = os.path.basename(name)
            if name[-4:] == '.zip':
                name = name[:-4]
            return name

        def is_really_module(name):
            for mname in MANIFEST_NAMES:
                if os.path.isfile(opj(dir, name, mname)):
                    return True

        return map(clean, filter(is_really_module, os.listdir(dir)))
