# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class GithubAnalysisRule(models.Model):
    _name = "github.analysis.rule.group"
    _description = "Github Analysis Rule Group"

    name = fields.Char(string="Name", required=True)
