# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# Copyright 2020-2023 Tecnativa - Víctor Martínez
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from odoo import api, fields, models
from odoo.modules.module import get_manifest

# Hard define this value to make this module working with or without
# the patch (that backports V10 manifests analysis code.
MANIFEST_NAMES = ("__manifest__.py", "__openerp__.py")

_logger = logging.getLogger(__name__)


class GithubRepositoryBranch(models.Model):
    _inherit = ["github.repository.branch", "abstract.action.mixin"]
    _name = "github.repository.branch"

    module_paths = fields.Text(
        help="Set here extra relative paths"
        " you want to scan to find modules. If not set, root path will be"
        " scanned. One repository per line. Example:\n"
        "./addons/\n"
        "./openerp/addons/",
    )

    module_version_ids = fields.One2many(
        comodel_name="odoo.module.version",
        inverse_name="repository_branch_id",
        string="Module Versions",
    )

    module_version_qty = fields.Integer(
        string="Number of Module Versions", compute="_compute_module_version_qty"
    )

    runbot_url = fields.Char(string="Runbot URL", compute="_compute_runbot_url")

    module_version_analysis_rule_info_ids = fields.Many2many(
        string="Analysis Rule Info ids (module version)",
        comodel_name="odoo.module.version.rule.info",
        compute="_compute_module_version_analysis_rule_info_ids",
        relation="rule_info_module_version_rel",
        column1="repository_branch_id",
        column2="module_version_id",
        readonly=True,
    )

    @api.depends("module_version_ids")
    def _compute_module_version_analysis_rule_info_ids(self):
        self.ensure_one()
        self.module_version_analysis_rule_info_ids = self.env[
            "odoo.module.version.rule.info"
        ].search(
            [
                ("module_version_id", "in", self.module_version_ids.ids),
                ("repository_branch_id", "=", self.id),
            ]
        )

    # Compute Section
    @api.depends(
        "name", "repository_id.runbot_id_external", "organization_id.runbot_url_pattern"
    )
    def _compute_runbot_url(self):
        for branch in self:
            if not branch.repository_id.runbot_id_external:
                branch.runbot_url = False
            else:
                branch.runbot_url = branch.organization_id.runbot_url_pattern.format(
                    runbot_id_external=str(branch.repository_id.runbot_id_external),
                    branch_name=branch.name,
                )

    @api.depends("module_version_ids", "module_version_ids.repository_branch_id")
    def _compute_module_version_qty(self):
        for repository_branch in self:
            repository_branch.module_version_qty = len(
                repository_branch.module_version_ids
            )

    # Custom Section
    @api.model
    def _set_state_to_analyze(self):
        """function called when the module is installed to set all branches
        to analyze again.
        """
        branches = self.search([("state", "=", "analyzed")])
        branches.write({"state": "to_analyze"})

    def _get_module_paths(self):
        # Compute path(s) to analyze
        self.ensure_one()
        if self.module_paths:
            paths = []
            for path in self.module_paths.split("\n"):
                if path.strip():
                    paths.append(os.path.join(self.local_path, path))
        else:
            paths = [self.local_path]
        return paths

    def analyze_code_one(self):
        # Change log level to avoid warning, when parsing odoo manifests
        logger1 = logging.getLogger("openerp.modules.module")
        logger2 = logging.getLogger("openerp.addons.base.module.module")
        currentLevel1 = logger1.level
        currentLevel2 = logger2.level
        logger1.setLevel(logging.ERROR)
        logger2.setLevel(logging.ERROR)

        try:
            paths = self._get_module_paths()
            # Scan each path, if exists
            for path in paths:
                if not os.path.exists(path):
                    _logger.warning(
                        "Unable to analyse %s. Source code not found.", path
                    )
                else:
                    # Analyze folders and create module versions
                    _logger.info("Analyzing repository %s ...", path)
                    for module_name in self.listdir(path):
                        self._analyze_module_name(path, module_name)
        finally:
            # Reset Original level for module logger
            logger1.setLevel(currentLevel1)
            logger2.setLevel(currentLevel2)
        return super().analyze_code_one()

    # Copy Paste from Odoo Core
    # This function is for the time being in another function.
    # (Ref: openerp/modules/module.py)
    def listdir(self, directory):
        def clean(name):
            name = os.path.basename(name)
            if name[-4:] == ".zip":
                name = name[:-4]
            return name

        def is_really_module(name):
            for mname in MANIFEST_NAMES:
                if os.path.isfile(os.path.join(directory, name, mname)):
                    return True

        return map(clean, filter(is_really_module, os.listdir(directory)))

    def _process_analysis_rule_info(self, rule, cloc_response):
        """Overwrite this method so that rules that have addons are processed by each
        module to obtain information from each one."""
        if rule.has_odoo_addons:
            for module_version in self.module_version_ids:
                self._process_analysis_rule_info_module_version(
                    rule, module_version, cloc_response
                )
        else:
            return super()._process_analysis_rule_info(rule, cloc_response)

    def _process_analysis_rule_info_module_version(
        self, rule, module_version, cloc_response
    ):
        """Process to specific rule + module version (Create or update info record)."""
        analysis_rule_item = module_version.analysis_rule_info_ids.filtered(
            lambda x: x.analysis_rule_id == rule and x.repository_branch_id == self
        )
        vals = self._prepare_analysis_module_version_rule_info_vals(
            rule, module_version, cloc_response
        )
        # Do not create lines if no file has been scanned
        if vals["scanned_files"] == 0:
            return False
        if analysis_rule_item:
            analysis_rule_item.write(vals)
        else:
            module_version.analysis_rule_info_ids = [(0, 0, vals)]

    def _prepare_analysis_module_version_rule_info_vals(
        self, rule, module_version, cloc_response
    ):
        """Prepare the analysis information values of a rule + module version."""
        res = self._operation_analysis_rule_by_module_version(
            rule, module_version, cloc_response
        )
        return {
            "analysis_rule_id": rule.id,
            "repository_branch_id": self.id,
            "module_version_id": module_version.id,
            "code_count": res["code"],
            "documentation_count": res["documentation"],
            "empty_count": res["empty"],
            "scanned_files": len(res["paths"]),
        }

    def _operation_analysis_rule_by_module_version(
        self, rule, module_version, cloc_response
    ):
        """This function (similar to _operation_analysis_rule() of github_connector)
        processes the result of cloc and defines the values for the corresponding rule
        and module version.
        The matchs that are used have the complete path, for that reason we set
        path=False is passed to the _action_analysis_process_cloc() method."""
        matchs = []
        full_path = module_version.full_module_path
        if rule.has_odoo_addons and rule.manifest_key_ids:
            manifest_keys_find = module_version.manifest_key_ids.filtered(
                lambda x: x.id in rule.manifest_key_ids.ids
            )
            module_info = get_manifest(module_version.technical_name, full_path)
            spec = rule._set_spec(rule.paths.splitlines())
            for manifest_key_find in manifest_keys_find:
                if manifest_key_find.name in module_info:
                    key_paths = module_info[manifest_key_find.name]
                    path_items = []
                    for key_path in key_paths:
                        path_items.append("{}/{}".format(full_path, key_path))
                    matchs += spec.match_files(path_items)
        else:
            matchs = rule._get_matches(full_path)
        return self._action_analysis_process_cloc(False, matchs, cloc_response)

    def _analyze_module_name(self, path, module_name):
        self.ensure_one()
        module_version_obj = self.env["odoo.module.version"]
        try:
            full_module_path = os.path.join(path, module_name)
            module_info = get_manifest(module_name, full_module_path)
            # Create module version, if the module is installable
            # in the serie
            if module_info.get("installable", False):
                module_info["technical_name"] = module_name
                module_version_obj.create_or_update_from_manifest(
                    module_info, self, full_module_path
                )
        except Exception as e:
            _logger.error(
                "Cannot process module with name %s, error " "is: %s", module_name, e
            )
