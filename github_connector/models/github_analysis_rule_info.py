# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class GithubAnalysisRuleInfoMixin(models.AbstractModel):
    _name = "github.analysis.rule.info.mixin"
    _description = "Github Analysis Rule Mixin"

    analysis_rule_id = fields.Many2one(
        string="Analysis Rule",
        comodel_name="github.analysis.rule",
        ondelete="cascade",
    )
    group_id = fields.Many2one(
        string="Group", related="analysis_rule_id.group_id", readonly=True
    )
    code_count = fields.Integer(string="# Code")
    documentation_count = fields.Integer(string="# Doc.")
    empty_count = fields.Integer(string="# Empty")
    string_count = fields.Integer(string="# String")
    total_count = fields.Integer(
        string="# Total", store=True, compute="_compute_total_count"
    )
    scanned_files = fields.Integer()

    @api.depends("code_count", "documentation_count", "empty_count", "string_count")
    def _compute_total_count(self):
        for item in self:
            item.total_count = (
                item.code_count
                + item.documentation_count
                + item.empty_count
                + item.string_count
            )
