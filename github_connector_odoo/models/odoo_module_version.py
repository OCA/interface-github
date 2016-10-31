# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from docutils.core import publish_string

from openerp import models, fields, api, _
from openerp.tools import html_sanitize
from openerp.addons.base.module.module import MyWriter


class OdooModuleVersion(models.Model):
    _name = 'odoo.module.version'
    _order = 'name, technical_name'

    # Constant Section
    _SETTING_OVERRIDES = {
        'embed_stylesheet': False,
        'doctitle_xform': False,
        'output_encoding': 'unicode',
        'xml_declaration': False,
    }

    # Column Section
    name = fields.Char(string='Name', readonly=True, select=True)

    technical_name = fields.Char(
        string='Technical Name', readonly=True, select=True,
        help="Technical Name of the Module. (Folder name)")

    complete_name = fields.Char(
        string='Complete Name', compute='_compute_complete_name', store=True)

    auto_install = fields.Boolean(string='Auto Install', readonly=True)

    icon = fields.Char(string='Icon Path (Manifest)', readonly=True)

    module_id = fields.Many2one(
        comodel_name='odoo.module', string='Module', required=True,
        ondelete='cascade', select=True, auto_join=True, readonly=True)

    repository_branch_id = fields.Many2one(
        comodel_name='github.repository.branch', string='Repository Branch',
        readonly=True, required=True, ondelete='cascade')

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository', readonly=True,
        related='repository_branch_id.repository_id', store=True)

    organization_serie_id = fields.Many2one(
        comodel_name='github.organization.serie', string='Organization Serie',
        compute='_compute_organization_serie_id', readonly=True, store=True)

    license = fields.Char(string='License (Manifest)', readonly=True)

    license_id = fields.Many2one(
        comodel_name='odoo.license', string='License', readonly=True,
        compute='_compute_license_id', store=True)

    summary = fields.Char(string='Summary (Manifest)', readonly=True)

    depends = fields.Char(string='Dependencies (Manifest)', readonly=True)

    dependency_module_ids = fields.Many2many(
        comodel_name='odoo.module', string='Dependencies',
        relation='module_version_dependency_rel', column1='module_version_id',
        column2='dependency_module_id',
        compute='_compute_dependency_module_ids', store=True)

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
        column1='module_version_id', column2='author_id',
        compute='_compute_author_ids', store=True)

    lib_python_ids = fields.Many2many(
        comodel_name='odoo.lib.python', string='Python Lib Dependencies',
        relation='module_version_lib_python_rel', column1='module_version_id',
        column2='lib_python_id', multi='lib', compute='_compute_lib',
        store=True)

    lib_bin_ids = fields.Many2many(
        comodel_name='odoo.lib.bin', string='Bin Lib Dependencies',
        relation='module_version_lib_bin_rel', column1='module_version_id',
        column2='lib_bin_id', multi='lib', compute='_compute_lib', store=True)

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
        modules = []
        for version in self:
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
            my_eval = eval(version.external_dependencies)
            for python_name in my_eval.get('python', []):
                python_libs.append(
                    lib_python_obj.create_if_not_exist(python_name))
            for bin_name in my_eval.get('bin', []):
                bin_libs.append(
                    lib_bin_obj.create_if_not_exist(bin_name))

            version.lib_python_ids = [x.id for x in python_libs]
            version.lib_bin_ids = [x.id for x in bin_libs]

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
    def _compute_author_ids(self):
        odoo_author_obj = self.env['odoo.author']
        for version in self:
            author_ids = []
            for item in version.author.split(','):
                if item:
                    author_ids.append(
                        odoo_author_obj.create_if_not_exist(item.strip()).id)
            version.author_ids = author_ids

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
            module_version.organization_serie_id = res and res[0].id or False

    # Custom Section
    @api.model
    def manifest_2_odoo(self, info, repository_branch, module):
        author_list =\
            (type(info['author']) == list) and info['author'] or\
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
    def create_or_update_from_manifest(self, info, repository_branch):
        module_obj = self.env['odoo.module']
        module_version = self.search([
            ('technical_name', '=', info['technical_name']),
            ('repository_branch_id', '=', repository_branch.id)])

        if not module_version:
            # Create new module version
            module = module_obj.create_if_not_exist(info['technical_name'])
            module_version.create(
                self.manifest_2_odoo(info, repository_branch, module))
        else:
            # Update module Version
            value = self.manifest_2_odoo(
                info, repository_branch, module_version.module_id)
            module_version.write(value)
