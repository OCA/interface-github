# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, tools


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
    string_count = fields.Integer(string="# String")
    total_count = fields.Integer(string="# Total")
    scanned_files = fields.Integer()

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        if fields is None:
            fields = {}
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            min(grbri.id) as id,
            gar.id as analysis_rule_id,
            garg.id as group_id,
            grb.id as repository_branch_id,
            gr.id as repository_id,
            gos.id as organization_serie_id,
            sum(grbri.code_count) as code_count,
            sum(grbri.documentation_count) as documentation_count,
            sum(grbri.string_count) as string_count,
            sum(grbri.empty_count) as empty_count,
            sum(grbri.total_count) as total_count,
            sum(grbri.scanned_files) as scanned_files
        """

        from_ = (
            """
                github_repository_branch_rule_info as grbri
                left join github_analysis_rule as gar on grbri.analysis_rule_id = gar.id
                left join github_analysis_rule_group as garg on gar.group_id = garg.id
                left join github_repository_branch as grb
                on grbri.repository_branch_id = grb.id
                left join github_organization_serie as gos
                on grb.organization_serie_id = gos.id
                left join github_repository as gr on grb.repository_id = gr.id
                %s
        """
            % from_clause
        )

        groupby_ = """
            gar.id,
            garg.id,
            grb.id,
            gr.id,
            gos.id %s
        """ % (
            groupby
        )

        return "{} (SELECT {} FROM {} WHERE grbri.id > 0 GROUP BY {})".format(
            with_,
            select_,
            from_,
            groupby_,
        )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # pylint: disable=E8103
        self.env.cr.execute(
            """CREATE or REPLACE VIEW {} as ({})""".format(self._table, self._query())
        )
