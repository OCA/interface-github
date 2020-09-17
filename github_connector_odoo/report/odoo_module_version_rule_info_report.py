# Copyright (C) 2020: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, tools


class OdooModuleVersionRuleInfoReport(models.Model):
    _name = "odoo.module.version.rule.info.report"
    _description = "Odoo Module Version Rule Info Report"
    _auto = False

    analysis_rule_id = fields.Many2one(
        string="Analysis Rule id",
        comodel_name="github.analysis.rule",
    )
    group_id = fields.Many2one(
        string="Group id", comodel_name="github.analysis.rule.group"
    )
    repository_branch_id = fields.Many2one(
        string="Repository Branch",
        comodel_name="github.repository.branch",
    )
    module_version_id = fields.Many2one(
        string="Module Version",
        comodel_name="odoo.module.version",
    )
    module_version_name = fields.Char(string="Module Version name")
    organization_serie_id = fields.Many2one(
        string="Organization serie",
        comodel_name="github.organization.serie",
    )
    code_count = fields.Integer(string="Code Count")
    documentation_count = fields.Integer(string="Documentation Count")
    empty_count = fields.Integer(string="Empty Count")
    string_count = fields.Integer(string="String Count")
    total_count = fields.Integer(string="Total Count")
    scanned_files = fields.Integer(string="Scanned files")

    def init(self):
        tools.drop_view_if_exists(self._cr, "odoo_module_version_rule_info_report")
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW odoo_module_version_rule_info_report AS (
                SELECT
                MIN(omvri.id) AS id,
                gar.id AS analysis_rule_id,
                garg.id AS group_id,
                gos.id AS organization_serie_id,
                grb.id AS repository_branch_id,
                omv.id AS module_version_id,
                omv.name AS module_version_name,
                SUM(omvri.code_count) AS code_count,
                SUM(omvri.documentation_count) AS documentation_count,
                SUM(omvri.string_count) AS string_count,
                SUM(omvri.empty_count) AS empty_count,
                SUM(omvri.total_count) AS total_count,
                SUM(omvri.scanned_files) AS scanned_files
                FROM odoo_module_version_rule_info AS omvri
                LEFT JOIN github_analysis_rule AS gar ON omvri.analysis_rule_id = gar.id
                LEFT JOIN github_analysis_rule_group AS garg ON gar.group_id = garg.id
                LEFT JOIN github_repository_branch AS grb
                ON omvri.repository_branch_id = grb.id
                LEFT JOIN odoo_module_version AS omv ON omvri.module_version_id = omv.id
                LEFT JOIN github_organization_serie AS gos
                ON omv.organization_serie_id = gos.id
                WHERE omvri.id > 0
                GROUP BY gar.id, garg.id, omv.id, omv.name, gos.id, grb.id
        )"""
        )
