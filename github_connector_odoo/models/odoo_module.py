# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.tools import html_sanitize


class OdooModule(models.Model):
    _inherit = "abstract.action.mixin"
    _name = "odoo.module"
    _description = "Odoo Module"
    _order = "technical_name, name"

    # Column Section
    name = fields.Char(
        string="Name", store=True, readonly=True, compute="_compute_name"
    )

    technical_name = fields.Char(
        string="Technical Name", index=True, required=True, readonly=True
    )

    module_version_ids = fields.One2many(
        comodel_name="odoo.module.version",
        inverse_name="module_id",
        string="Versions",
        readonly=True,
    )

    module_version_qty = fields.Integer(
        string="Number of Module Versions",
        compute="_compute_module_version_qty",
        store=True,
    )

    author_ids = fields.Many2many(
        string="Authors",
        comodel_name="odoo.author",
        compute="_compute_author",
        relation="github_module_author_rel",
        column1="module_id",
        column2="author_id",
        store=True,
    )

    author_ids_description = fields.Char(
        string="Authors (Text)", compute="_compute_author", store=True
    )

    organization_serie_ids = fields.Many2many(
        string="Series",
        comodel_name="github.organization.serie",
        compute="_compute_organization_serie",
        store=True,
        relation="github_module_organization_serie_rel",
        column1="module_id",
        column2="organization_serie_id",
    )

    organization_serie_ids_description = fields.Char(
        string="Series (Text)",
        store=True,
        compute="_compute_organization_serie",
    )

    description_rst = fields.Char(
        string="RST Description of the last Version",
        store=True,
        readonly=True,
        compute="_compute_description",
    )

    description_rst_html = fields.Html(
        string="HTML of the RST Description of the last Version",
        store=True,
        readonly=True,
        compute="_compute_description",
    )

    dependence_module_version_ids = fields.Many2many(
        comodel_name="odoo.module.version",
        string="Module Versions that depend on this module",
        relation="module_version_dependency_rel",
        column1="dependency_module_id",
        column2="module_version_id",
    )

    dependence_module_version_qty = fields.Integer(
        string="Number of Module Versions that depend on this module",
        compute="_compute_dependence_module_version_qty",
        store=True,
    )

    image = fields.Binary(
        string="Icon Image", compute="_compute_image", store=True, attachment=True
    )

    # Compute Section
    @api.depends("module_version_ids.image")
    def _compute_image(self):
        module_version_obj = self.env["odoo.module.version"]
        for module in self:
            version_ids = module.module_version_ids.ids
            last_version = module_version_obj.search(
                [("id", "in", version_ids)], order="organization_serie_id desc", limit=1
            )
            module.image = last_version and last_version.image

    @api.depends("technical_name", "module_version_ids.name")
    def _compute_name(self):
        module_version_obj = self.env["odoo.module.version"]
        for module in self:
            version_ids = module.module_version_ids.ids
            last_version = module_version_obj.search(
                [("id", "in", version_ids)], order="organization_serie_id desc", limit=1
            )
            if last_version:
                module.name = last_version.name
            else:
                module.name = module.technical_name

    @api.depends("module_version_ids", "module_version_ids.description_rst_html")
    def _compute_description(self):
        module_version_obj = self.env["odoo.module.version"]
        for module in self:
            version_ids = module.module_version_ids.ids
            last_version = module_version_obj.search(
                [("id", "in", version_ids)], order="organization_serie_id desc", limit=1
            )
            if last_version:
                module.description_rst = last_version.description_rst
                module.description_rst_html = last_version.description_rst_html
            else:
                module.description_rst = ""
                module.description_rst_html = html_sanitize(
                    "<h1 style='color:gray;'>" + _("No Version Found") + "</h1>"
                )

    @api.depends("dependence_module_version_ids.dependency_module_ids")
    def _compute_dependence_module_version_qty(self):
        for module in self:
            module.dependence_module_version_qty = len(
                module.dependence_module_version_ids
            )

    @api.depends("module_version_ids")
    def _compute_module_version_qty(self):
        for module in self:
            module.module_version_qty = len(module.module_version_ids)

    @api.depends("module_version_ids.author_ids")
    def _compute_author(self):
        for module in self:
            authors = []
            for version in module.module_version_ids:
                authors += version.author_ids
            authors = set(authors)
            module.author_ids = [x.id for x in authors]
            module.author_ids_description = ", ".join(sorted(x.name for x in authors))

    @api.depends("module_version_ids.organization_serie_id")
    def _compute_organization_serie(self):
        for module in self:
            organization_series = []
            for version in module.module_version_ids:
                organization_series += version.organization_serie_id
            organization_series = set(organization_series)
            module.organization_serie_ids = [x.id for x in organization_series]
            module.organization_serie_ids_description = " - ".join(
                [x.name for x in sorted(organization_series, key=lambda x: x.sequence)]
            )

    # Custom Section
    @api.model
    def create_if_not_exist(self, technical_name):
        module = self.search([("technical_name", "=", technical_name)])
        if not module:
            module = self.create({"technical_name": technical_name})
        return module

    def name_get(self):
        return [(module.id, module.technical_name) for module in self]
