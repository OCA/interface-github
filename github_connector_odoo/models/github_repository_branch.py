# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from os.path import join as opj

from odoo import api, fields, models

from odoo.modules import load_information_from_description_file

# Hard define this value to make this module working with or without
# the patch (that backports V10 manifests analysis code.
MANIFEST_NAMES = ('__manifest__.py', '__openerp__.py')

_logger = logging.getLogger(__name__)


class GithubRepositoryBranch(models.Model):
    _inherit = ['github.repository.branch']

    module_paths = fields.Text(
        string='Module Paths', help="Set here extra relative paths"
        " you want to scan to find modules. If not set, root path will be"
        " scanned. One repository per line. Example:\n"
        "./addons/\n"
        "./openerp/addons/")

    module_version_ids = fields.One2many(
        comodel_name='odoo.module.version',
        inverse_name='repository_branch_id', string='Module Versions')

    module_version_qty = fields.Integer(
        string='Number of Module Versions',
        compute='_compute_module_version_qty')

    runbot_url = fields.Char(
        string='Runbot URL', compute='_compute_runbot_url')

    # Compute Section
    @api.multi
    @api.depends(
        'name', 'repository_id.runbot_id_external',
        'organization_id.runbot_url_pattern')
    def _compute_runbot_url(self):
        for branch in self:
            if not branch.repository_id.runbot_id_external:
                branch.runbot_url = False
            else:
                branch.runbot_url =\
                    branch.organization_id.runbot_url_pattern.format(
                        runbot_id_external=str(
                            branch.repository_id.runbot_id_external),
                        branch_name=branch.name)

    @api.multi
    @api.depends(
        'module_version_ids', 'module_version_ids.repository_branch_id')
    def _compute_module_version_qty(self):
        for repository_branch in self:
            repository_branch.module_version_qty =\
                len(repository_branch.module_version_ids)

    # Custom Section
    @api.model
    def _set_state_to_analyze(self):
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
                        paths.append(os.path.join(branch.local_path, path))
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
                    _logger.info("Analyzing repository %s ..." % path)
                    for module_name in self.listdir(path):
                        self._analyze_module_name(path, module_name, branch)
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

    def _analyze_module_name(self, path, module_name, branch):
        module_version_obj = self.env['odoo.module.version']
        try:
            full_module_path = os.path.join(path, module_name)
            module_info = load_information_from_description_file(
                module_name, full_module_path)
            # Create module version, if the module is installable
            # in the serie
            if module_info.get('installable', False):
                module_info['technical_name'] = module_name
                module_version_obj.create_or_update_from_manifest(
                    module_info, branch, full_module_path)
        except Exception as e:
            _logger.error('Cannot process module with name %s, error '
                          'is: %s' % (module_name, e))
