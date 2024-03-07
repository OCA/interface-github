# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import sql

from odoo import api, fields, models, tools


class GithubRepositoryBranchRuleInfoReport(models.Model):
    _inherit = "github.analysis.rule"
    _name = "github.repository.branch.rule.info.report"
    _description = "Github Repository Branch Rule Info Report"
    _auto = False

    analysis_rule_id = fields.Many2one(
        string="Analysis Rule",
        comodel_name="github.analysis.rule",
    )
    group_id = fields.Many2one(
        string="Group", related="analysis_rule_id.group_id", readonly=True
    )
    repository_branch_id = fields.Many2one(
        string="Repository Branch",
        comodel_name="github.repository.branch",
    )
    repository_id = fields.Many2one(
        string="Repository",
        comodel_name="github.repository",
    )
    organization_serie_id = fields.Many2one(
        string="Organization serie",
        comodel_name="github.organization.serie",
    )
    code_count = fields.Integer(string="# Code")
    documentation_count = fields.Integer(string="# Documentation")
    empty_count = fields.Integer(string="# Empty")
    total_count = fields.Integer(string="# Total")
    scanned_files = fields.Integer()

    @property
    def _table_query(self):
        return "%s %s %s" % (self._select(), self._from(), self._group_by())

    @api.model
    def _select(self):
        return """
            SELECT
                min(grbri.id) as id,
                gar.id as analysis_rule_id,
                garg.id as group_id,
                grb.id as repository_branch_id,
                gr.id as repository_id,
                gos.id as organization_serie_id,
                sum(grbri.code_count) as code_count,
                sum(grbri.documentation_count) as documentation_count,
                sum(grbri.empty_count) as empty_count,
                sum(grbri.total_count) as total_count,
                sum(grbri.scanned_files) as scanned_files
        """

    @api.model
    def _from(self):
        return """
            FROM github_repository_branch_rule_info as grbri
                LEFT JOIN github_analysis_rule as gar ON grbri.analysis_rule_id = gar.id
                LEFT JOIN github_analysis_rule_group as garg ON gar.group_id = garg.id
                LEFT JOIN github_repository_branch as grb ON grbri.repository_branch_id = grb.id
                LEFT JOIN github_organization_serie as gos ON grb.organization_serie_id = gos.id
                LEFT JOIN github_repository as gr ON grb.repository_id = gr.id
        """

    def _group_by(self):
        return """
            GROUP BY
                gar.id,
                garg.id,
                grb.id,
                gr.id,
                gos.id
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            sql.SQL("CREATE or REPLACE VIEW {} as ({})").format(
                sql.Identifier(self._table), sql.SQL(self._table_query)
            )
        )
