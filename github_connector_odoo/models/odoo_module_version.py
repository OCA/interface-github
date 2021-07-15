# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from docutils.core import publish_string

from openerp import api, fields, models, tools, _
from openerp.tools import html_sanitize
from openerp.addons.base.module.module import MyWriter
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class OdooModuleVersion(models.Model):
    _name = 'odoo.module.version'
    _order = 'name, technical_name'

    _ICON_PATH = [
        'static/src/img/',
        'static/description/',
    ]

    # Constant Section
    _SETTING_OVERRIDES = {
        'embed_stylesheet': False,
        'doctitle_xform': False,
        'output_encoding': 'unicode',
        'xml_declaration': False,
    }

    _ODOO_TYPE_SELECTION = [
        ('verticalization', 'Vertical Solutions'),
        ('localization', 'Localization'),
        ('connector', 'Connector'),
        ('other', 'Other'),
    ]

    # Column Section
    name = fields.Char(string='Name', readonly=True, index=True)

    technical_name = fields.Char(
        string='Technical Name', readonly=True, index=True,
        help="Technical Name of the Module (Folder name).")

    complete_name = fields.Char(
        string='Complete Name', compute='_compute_complete_name', store=True)

    auto_install = fields.Boolean(string='Auto Install', readonly=True)

    icon = fields.Char(string='Icon Path (Manifest)', readonly=True)

    module_id = fields.Many2one(
        comodel_name='odoo.module', string='Module', required=True,
        ondelete='cascade', index=True, auto_join=True, readonly=True)

    repository_branch_id = fields.Many2one(
        comodel_name='github.repository.branch', string='Repository Branch',
        readonly=True, required=True, ondelete='cascade')

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository', readonly=True,
        related='repository_branch_id.repository_id', store=True)

    organization_serie_id = fields.Many2one(
        comodel_name='github.organization.serie',
        string='Organization Serie', readonly=True, store=True,
        compute='_compute_organization_serie_id')

    license = fields.Char(string='License (Manifest)', readonly=True)

    license_id = fields.Many2one(
        comodel_name='odoo.license', string='License', readonly=True,
        compute='_compute_license_id', store=True)

    summary = fields.Char(string='Summary (Manifest)', readonly=True)

    depends = fields.Char(string='Dependencies (Manifest)', readonly=True)

    dependency_module_ids = fields.Many2many(
        comodel_name='odoo.module', string='Dependencies',
        relation='module_version_dependency_rel', column1='module_version_id',
        column2='dependency_module_id', store=True,
        compute='_compute_dependency_module_ids')

    website = fields.Char(string='Website (Manifest)', readonly=True)

    external_dependencies = fields.Char(
        string='External Dependencies (Manifest)', readonly=True)

    description_rst = fields.Char(
        string='RST Description (Manifest)', readonly=True)

    description_rst_html = fields.Html(
        string='HTML the RST Description', readonly=True,
        compute='_compute_description_rst_html', store=True)

    version = fields.Char(string='Version (Manifest)', readonly=True)

    author = fields.Char(string='Author (Manifest)', readonly=True)

    author_ids = fields.Many2many(
        string='Authors', comodel_name='odoo.author',
        relation='github_module_version_author_rel',
        column1='module_version_id', column2='author_id', multi='author',
        compute='_compute_author', store=True)

    author_ids_description = fields.Char(
        string='Authors (Text)', compute='_compute_author', multi='author',
        store=True)

    lib_python_ids = fields.Many2many(
        comodel_name='odoo.lib.python', string='Python Lib Dependencies',
        relation='module_version_lib_python_rel', column1='module_version_id',
        column2='lib_python_id', multi='lib', compute='_compute_lib',
        store=True)

    lib_python_ids_description = fields.Char(
        string='Python Lib Dependencies (Text)', compute='_compute_lib',
        multi='lib', store=True)

    lib_bin_ids = fields.Many2many(
        comodel_name='odoo.lib.bin', string='Bin Lib Dependencies',
        relation='module_version_lib_bin_rel', column1='module_version_id',
        column2='lib_bin_id', multi='lib', compute='_compute_lib', store=True)

    lib_bin_ids_description = fields.Char(
        string='Bin Lib Dependencies (Text)', compute='_compute_lib',
        multi='lib', store=True)

    odoo_type = fields.Selection(
        string='Odoo Type', selection=_ODOO_TYPE_SELECTION, store=True,
        compute='_compute_odoo_type')

    image = fields.Binary(string='Icon Image', reaonly=True)

    github_url = fields.Char(
        string='Github URL', compute='_compute_github_url', store=True,
        readonly=True)

    # Overload Section
    @api.multi
    def unlink(self):
        # Analyzed repository branches should be reanalyzed
        if not self._context.get('dont_change_repository_branch_state', False):
            repository_branch_obj = self.env['github.repository.branch']
            repository_branch_obj.search([
                ('id', 'in', self.mapped('repository_branch_id').ids),
                ('state', '=', 'analyzed')]).write({'state': 'to_analyze'})
        return super(OdooModuleVersion, self).unlink()

    # Compute Section
    @api.multi
    @api.depends(
        'technical_name', 'repository_id.organization_id.github_login',
        'repository_id.name', 'repository_branch_id.name')
    def _compute_github_url(self):
        for version in self:
            version.github_url = "https://github.com/{organization_name}/"\
                "{repository_name}/tree/{branch_name}/{module_name}".format(
                    organization_name=version.
                    repository_id.organization_id.github_login,
                    repository_name=version.repository_id.name,
                    branch_name=version.repository_branch_id.name,
                    module_name=version.technical_name)

    @api.depends('repository_branch_id.repository_id.name')
    def _compute_odoo_type(self):
        for version in self:
            repository_name = version.repository_branch_id.repository_id.name
            if repository_name.startswith('l10n-'):
                version.odoo_type = 'localization'
            elif repository_name.startswith('connector-'):
                version.odoo_type = 'connector'
            elif repository_name.startswith('vertical-'):
                version.odoo_type = 'verticalization'
            else:
                version.odoo_type = 'other'

    @api.multi
    @api.depends('technical_name', 'repository_branch_id.complete_name')
    def _compute_complete_name(self):
        for version in self:
            version.complete_name =\
                version.repository_branch_id.complete_name +\
                '/' + version.technical_name

    @api.multi
    @api.depends('description_rst')
    def _compute_description_rst_html(self):
        for version in self:
            if version.description_rst:
                try:
                    output = publish_string(
                        source=version.description_rst,
                        settings_overrides=self._SETTING_OVERRIDES,
                        writer=MyWriter())
                except:
                    output =\
                        "<h1 style='color:red;'>" +\
                        _("Incorrect RST Description") +\
                        "</h1>"
            else:
                output = html_sanitize(
                    "<h1 style='color:gray;'>" +
                    _("No Version Found") +
                    "</h1>")
            version.description_rst_html = html_sanitize(output)

    @api.multi
    @api.depends('depends')
    def _compute_dependency_module_ids(self):
        module_obj = self.env['odoo.module']
        for version in self:
            modules = []
            for module_name in version.depends.split(','):
                if module_name:
                    # Weird case, some times 'depends' field is empty
                    modules.append(module_obj.create_if_not_exist(module_name))
            version.dependency_module_ids = [x.id for x in modules]

    @api.multi
    @api.depends('external_dependencies')
    def _compute_lib(self):
        lib_python_obj = self.env['odoo.lib.python']
        lib_bin_obj = self.env['odoo.lib.bin']
        for version in self:
            python_libs = []
            bin_libs = []
            my_eval = safe_eval(version.external_dependencies)
            for python_name in my_eval.get('python', []):
                python_libs.append(
                    lib_python_obj.create_if_not_exist(python_name))
            for bin_name in my_eval.get('bin', []):
                bin_libs.append(
                    lib_bin_obj.create_if_not_exist(bin_name))

            version.lib_python_ids = [x.id for x in python_libs]
            version.lib_python_ids_description =\
                ', '.join(sorted([x.name for x in python_libs]))
            version.lib_bin_ids = [x.id for x in bin_libs]
            version.lib_bin_ids_description =\
                ', '.join(sorted([x.name for x in bin_libs]))

    @api.multi
    @api.depends('license')
    def _compute_license_id(self):
        license_obj = self.env['odoo.license']
        for version in self:
            if version.license:
                version.license_id =\
                    license_obj.create_if_not_exist(version.license).id

    @api.multi
    @api.depends('author')
    def _compute_author(self):
        odoo_author_obj = self.env['odoo.author']
        for version in self:
            authors = []
            for item in [x.strip() for x in version.author.split(',')]:
                if item and item != version.repository_id.organization_id.\
                        default_author_text:
                    authors.append(
                        odoo_author_obj.create_if_not_exist(item))
            authors = set(authors)
            version.author_ids = [x.id for x in authors]
            version.author_ids_description =\
                ', '.join(sorted([x.name for x in authors]))

    @api.multi
    @api.depends(
        'repository_branch_id', 'repository_branch_id.organization_id',
        'repository_branch_id.organization_id.organization_serie_ids',
        'repository_branch_id.organization_id.organization_serie_ids.name')
    def _compute_organization_serie_id(self):
        organization_serie_obj = self.env['github.organization.serie']
        for module_version in self:
            res = organization_serie_obj.search([
                ('organization_id', '=',
                    module_version.repository_branch_id.organization_id.id),
                ('name', '=', module_version.repository_branch_id.name)])
            module_version.organization_serie_id =\
                res and res[0].id or False

    # Custom Section
    @api.model
    def manifest_2_odoo(self, info, repository_branch, module):
        author_list =\
            (type(info['author']) == list) and info['author'] or\
            (type(info['author']) == tuple) and [x for x in info['author']] or\
            info['author'].split(',')
        res = {
            'name': info['name'],
            'technical_name': info['technical_name'],
            'summary': info['summary'],
            'website': info['website'],
            'version': info['version'],
            'license': info['license'],
            'auto_install': info['auto_install'],
            'icon': info['icon'],
            'description_rst': info['description'],
            'external_dependencies': info.get('external_dependencies', {}),
            'author': ','.join(
                [x.strip() for x in sorted(author_list) if x.strip()]),
            'depends': ','.join([x for x in sorted(info['depends']) if x]),
            'repository_branch_id': repository_branch.id,
            'module_id': module.id,
        }
        return res

    @api.model
    def create_or_update_from_manifest(
            self, info, repository_branch, full_module_path):
        module_obj = self.env['odoo.module']
        module_version = self.search([
            ('technical_name', '=', str(info['technical_name'])),
            ('repository_branch_id', '=', repository_branch.id)])

        if not module_version:
            # Create new module version
            module = module_obj.create_if_not_exist(info['technical_name'])
            module_version = self.create(
                self.manifest_2_odoo(info, repository_branch, module))

        else:
            # Update module Version
            value = self.manifest_2_odoo(
                info, repository_branch, module_version.module_id)
            module_version.write(value)
        icon_path = False
        for current_icon_path in self._ICON_PATH:
            full_current_icon_path = os.path.join(
                full_module_path, current_icon_path, 'icon.png')
            if os.path.exists(full_current_icon_path):
                icon_path = full_current_icon_path
        if icon_path:
            resized_image = False
            try:
                with open(icon_path, 'rb') as f:
                    image = f.read()
                resized_image = tools.image_resize_image(
                    image.encode('base64'), size=(96, 96),
                    encoding='base64', filetype='PNG')
            except Exception:
                _logger.warn("Unable to read or resize %s" % icon_path)
            module_version.write({'image': resized_image})
