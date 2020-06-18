# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging
import os

from docutils.core import publish_string

from odoo import _, api, fields, models, tools
from odoo.tools import html_sanitize
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.ir_module import MyWriter

_logger = logging.getLogger(__name__)


class OdooModuleVersion(models.Model):
    _name = "odoo.module.version"
    _description = "Odoo Module Version"
    _order = "name, technical_name"

    _ICON_PATH = [
        "static/src/img/",
        "static/description/",
    ]

    # Constant Section
    _SETTING_OVERRIDES = {
        "embed_stylesheet": False,
        "doctitle_xform": False,
        "output_encoding": "unicode",
        "xml_declaration": False,
        "file_insertion_enabled": False,
        "raw_enabled": False,
    }

    _ODOO_TYPE_SELECTION = [
        ("verticalization", "Vertical Solutions"),
        ("localization", "Localization"),
        ("connector", "Connector"),
        ("other", "Other"),
    ]

    # Column Section
    name = fields.Char(string="Name", readonly=True, index=True)

    technical_name = fields.Char(
        string="Technical Name",
        readonly=True,
        index=True,
        help="Technical Name of the Module (Folder name).",
    )

    complete_name = fields.Char(
        string="Complete Name", compute="_compute_complete_name", store=True
    )

    auto_install = fields.Boolean(string="Auto Install", readonly=True)

    icon = fields.Char(string="Icon Path (Manifest)", readonly=True)

    module_id = fields.Many2one(
        comodel_name="odoo.module",
        string="Module",
        required=True,
        ondelete="cascade",
        index=True,
        auto_join=True,
        readonly=True,
    )

    repository_branch_id = fields.Many2one(
        comodel_name="github.repository.branch",
        string="Repository Branch",
        readonly=True,
        required=True,
        ondelete="cascade",
    )

    repository_id = fields.Many2one(
        comodel_name="github.repository",
        string="Repository",
        readonly=True,
        related="repository_branch_id.repository_id",
        store=True,
    )

    organization_serie_id = fields.Many2one(
        comodel_name="github.organization.serie",
        string="Organization Serie",
        readonly=True,
        store=True,
        compute="_compute_organization_serie_id",
    )

    license = fields.Char(string="License (Manifest)", readonly=True)

    license_id = fields.Many2one(
        comodel_name="odoo.license",
        string="License",
        readonly=True,
        compute="_compute_license_id",
        store=True,
    )

    summary = fields.Char(string="Summary (Manifest)", readonly=True)

    depends = fields.Char(string="Dependencies (Manifest)", readonly=True)

    dependency_module_ids = fields.Many2many(
        comodel_name="odoo.module",
        string="Dependencies",
        relation="module_version_dependency_rel",
        column1="module_version_id",
        column2="dependency_module_id",
        store=True,
        compute="_compute_dependency_module_ids",
    )

    website = fields.Char(string="Website (Manifest)", readonly=True)

    external_dependencies = fields.Char(
        string="External Dependencies (Manifest)", readonly=True
    )

    description_rst = fields.Char(string="RST Description (Manifest)", readonly=True)

    description_rst_html = fields.Html(
        string="HTML the RST Description",
        readonly=True,
        compute="_compute_description_rst_html",
        store=True,
    )

    version = fields.Char(string="Version (Manifest)", readonly=True)

    author = fields.Char(string="Author (Manifest)", readonly=True)

    author_ids = fields.Many2many(
        string="Authors",
        comodel_name="odoo.author",
        relation="github_module_version_author_rel",
        column1="module_version_id",
        column2="author_id",
        multi="author",
        compute="_compute_author",
        store=True,
    )

    author_ids_description = fields.Char(
        string="Authors (Text)", compute="_compute_author", multi="author", store=True
    )

    lib_python_ids = fields.Many2many(
        comodel_name="odoo.lib.python",
        string="Python Lib Dependencies",
        relation="module_version_lib_python_rel",
        column1="module_version_id",
        column2="lib_python_id",
        multi="lib",
        compute="_compute_lib",
        store=True,
    )

    lib_python_ids_description = fields.Char(
        string="Python Lib Dependencies (Text)",
        compute="_compute_lib",
        multi="lib",
        store=True,
    )

    lib_bin_ids = fields.Many2many(
        comodel_name="odoo.lib.bin",
        string="Bin Lib Dependencies",
        relation="module_version_lib_bin_rel",
        column1="module_version_id",
        column2="lib_bin_id",
        multi="lib",
        compute="_compute_lib",
        store=True,
    )

    lib_bin_ids_description = fields.Char(
        string="Bin Lib Dependencies (Text)",
        compute="_compute_lib",
        multi="lib",
        store=True,
    )

    odoo_type = fields.Selection(
        string="Odoo Type",
        selection=_ODOO_TYPE_SELECTION,
        store=True,
        compute="_compute_odoo_type",
    )

    image = fields.Binary(string="Icon Image", readonly=True, attachment=True)

    github_url = fields.Char(
        string="Github URL", compute="_compute_github_url", store=True, readonly=True
    )

    category_id = fields.Many2one(
        comodel_name="odoo.category", string="Category", readonly=True
    )

    full_module_path = fields.Char(string="Full Local Path to the module",)

    # Overload Section
    def unlink(self):
        # Analyzed repository branches should be reanalyzed
        if not self._context.get("dont_change_repository_branch_state", False):
            repository_branch_obj = self.env["github.repository.branch"]
            repository_branch_obj.search(
                [
                    ("id", "in", self.mapped("repository_branch_id").ids),
                    ("state", "=", "analyzed"),
                ]
            ).write({"state": "to_analyze"})
        return super(OdooModuleVersion, self).unlink()

    # Compute Section
    @api.depends(
        "repository_id.organization_id.github_login",
        "repository_id.name",
        "repository_branch_id.name",
        "repository_branch_id.local_path",
        "full_module_path",
    )
    def _compute_github_url(self):
        for version in self:
            repo_id = version.repository_id
            version.github_url = (
                "https://github.com/{organization_name}/"
                "{repository_name}/tree/{branch_name}/{rest_path}".format(
                    organization_name=repo_id.organization_id.github_login,
                    repository_name=repo_id.name,
                    branch_name=version.repository_branch_id.name,
                    rest_path=version.full_module_path[
                        len(version.repository_branch_id.local_path) + 1 :
                    ],
                )
            )

    @api.depends("repository_branch_id.repository_id.name")
    def _compute_odoo_type(self):
        for version in self:
            repository_name = version.repository_branch_id.repository_id.name
            if repository_name.startswith("l10n-"):
                version.odoo_type = "localization"
            elif repository_name.startswith("connector-"):
                version.odoo_type = "connector"
            elif repository_name.startswith("vertical-"):
                version.odoo_type = "verticalization"
            else:
                version.odoo_type = "other"

    @api.depends("technical_name", "repository_branch_id.complete_name")
    def _compute_complete_name(self):
        for version in self:
            version.complete_name = (
                version.repository_branch_id.complete_name
                + "/"
                + version.technical_name
            )

    @api.depends("description_rst")
    def _compute_description_rst_html(self):
        for version in self:
            if version.description_rst:
                try:
                    output = publish_string(
                        source=version.description_rst,
                        settings_overrides=self._SETTING_OVERRIDES,
                        writer=MyWriter(),
                    )
                except Exception:
                    output = (
                        "<h1 style='color:red;'>"
                        + _("Incorrect RST Description")
                        + "</h1>"
                    )
            else:
                output = html_sanitize(
                    "<h1 style='color:gray;'>" + _("No Version Found") + "</h1>"
                )
            version.description_rst_html = html_sanitize(output)

    @api.depends("depends")
    def _compute_dependency_module_ids(self):
        module_obj = self.env["odoo.module"]
        for version in self:
            modules = []
            for module_name in version.depends.split(","):
                if module_name:
                    # Weird case, some times 'depends' field is empty
                    modules.append(module_obj.create_if_not_exist(module_name))
            version.dependency_module_ids = [x.id for x in modules]

    @api.depends("external_dependencies")
    def _compute_lib(self):
        lib_python_obj = self.env["odoo.lib.python"]
        lib_bin_obj = self.env["odoo.lib.bin"]
        for version in self:
            python_libs = []
            bin_libs = []
            my_eval = safe_eval(version.external_dependencies)
            for python_name in my_eval.get("python", []):
                python_libs.append(lib_python_obj.create_if_not_exist(python_name))
            for bin_name in my_eval.get("bin", []):
                bin_libs.append(lib_bin_obj.create_if_not_exist(bin_name))

            version.lib_python_ids = [x.id for x in python_libs]
            version.lib_python_ids_description = ", ".join(
                sorted([x.name for x in python_libs])
            )
            version.lib_bin_ids = [x.id for x in bin_libs]
            version.lib_bin_ids_description = ", ".join(
                sorted([x.name for x in bin_libs])
            )

    @api.depends("license")
    def _compute_license_id(self):
        license_obj = self.env["odoo.license"]
        for version in self:
            if version.license:
                version.license_id = license_obj.create_if_not_exist(version.license).id

    @api.depends("author")
    def _compute_author(self):
        odoo_author_obj = self.env["odoo.author"]
        for version in self:
            authors = []
            for item in [x.strip() for x in version.author.split(",")]:
                if (
                    item
                    and item
                    != version.repository_id.organization_id.default_author_text
                ):
                    authors.append(odoo_author_obj.create_if_not_exist(item))
            authors = set(authors)
            version.author_ids = [x.id for x in authors]
            version.author_ids_description = ", ".join(
                sorted([x.name for x in authors])
            )

    @api.depends(
        "repository_branch_id",
        "repository_branch_id.organization_id",
        "repository_branch_id.organization_id.organization_serie_ids",
        "repository_branch_id.organization_id.organization_serie_ids.name",
    )
    def _compute_organization_serie_id(self):
        organization_serie_obj = self.env["github.organization.serie"]
        for module_version in self:
            res = organization_serie_obj.search(
                [
                    (
                        "organization_id",
                        "=",
                        module_version.repository_branch_id.organization_id.id,
                    ),
                    ("name", "=", module_version.repository_branch_id.name),
                ]
            )
            module_version.organization_serie_id = res and res[0].id or False

    @api.model
    def get_module_category(self, info):
        """Used to search the category of the module by the data given
        on the manifest.

        :param dict info: The parsed dictionary with the manifest data.
        :returns: recordset of the given category if exists.
        """
        category_obj = self.env["odoo.category"]
        category = info.get("category", False)
        other_categ = category_obj.search([("name", "=", "Other")], limit=1)
        if not category:
            return other_categ
        found_category = category_obj.search([("name", "=", category)], limit=1)
        return found_category or other_categ

    # Custom Section
    @api.model
    def manifest_2_odoo(self, info, repository_branch, module):
        author_list = (
            (type(info["author"]) == list)
            and info["author"]
            or (type(info["author"]) == tuple)
            and [x for x in info["author"]]
            or info["author"].split(",")
        )
        return {
            "name": info["name"],
            "technical_name": info["technical_name"],
            "summary": info["summary"],
            "website": info["website"],
            "version": info["version"],
            "license": info["license"],
            "auto_install": info["auto_install"],
            "icon": info["icon"],
            "description_rst": info["description"],
            "external_dependencies": info.get("external_dependencies", {}),
            "author": ",".join([x.strip() for x in sorted(author_list) if x.strip()]),
            "depends": ",".join([x for x in sorted(info["depends"]) if x]),
            "repository_branch_id": repository_branch.id,
            "module_id": module.id,
            "category_id": self.get_module_category(info).id or None,
        }

    @api.model
    def create_or_update_from_manifest(self, info, repository_branch, full_module_path):
        module_obj = self.env["odoo.module"]
        module_version = self.search(
            [
                ("technical_name", "=", str(info["technical_name"])),
                ("repository_branch_id", "=", repository_branch.id),
            ]
        )

        if not module_version:
            # Create new module version
            module = module_obj.create_if_not_exist(info["technical_name"])
            vals = self.manifest_2_odoo(info, repository_branch, module)
            vals["full_module_path"] = full_module_path
            module_version = self.create(vals)

        else:
            # Update module Version
            vals = self.manifest_2_odoo(
                info, repository_branch, module_version.module_id
            )
            vals["full_module_path"] = full_module_path
            module_version.write(vals)
        icon_path = False
        resize = False
        if info.get("images"):
            full_current_icon_path = os.path.join(
                full_module_path, info.get("images")[0]
            )
            if os.path.exists(full_current_icon_path):
                icon_path = full_current_icon_path
        else:
            for current_icon_path in self._ICON_PATH:
                full_current_icon_path = os.path.join(
                    full_module_path, current_icon_path, "icon.png"
                )
                if os.path.exists(full_current_icon_path):
                    icon_path = full_current_icon_path
                    resize = True
                    break
        if icon_path:
            image_enc = False
            try:
                with open(icon_path, "rb") as f:
                    image = f.read()
                image_enc = base64.b64encode(image)
                if resize:
                    image = tools.image.ImageProcess(image_enc, False)
                    image.resize(96, 96)
                    image_enc = image.image_base64(output_format="PNG")
            except Exception:
                _logger.warning("Unable to read or resize %s", icon_path)
            module_version.write({"image": image_enc})
        else:
            # Set the default icon
            try:
                with open(
                    os.path.join(os.path.dirname(__file__), "../data/oca.png"), "rb"
                ) as f:
                    image = base64.b64encode(f.read())
                    module_version.write({"image": image})
            except Exception as e:
                _logger.error("Unable to read the OCA icon image, error is %s", e)

    @api.model
    def cron_clean_odoo_module_version(self):
        module_versions = self.search([])
        module_versions.clean_odoo_module_version()

    def clean_odoo_module_version(self):
        for module_version in self:
            # Compute path(s) to analyze
            paths = module_version.repository_branch_id._get_module_paths()
            found = False
            for path in paths:
                module_ver_path = os.path.join(path, module_version.technical_name)
                if os.path.exists(module_ver_path):
                    found = True
                    continue
            if not found:
                module_version._process_clean_module_version()
        return True

    def _process_clean_module_version(self):
        for module_version in self:
            module_version.unlink()
        return True
