# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pathspec

from odoo import fields, models


class GithubAnalysisRule(models.Model):
    _name = "github.analysis.rule"
    _description = "Github Analysis Rule"

    name = fields.Char(required=True)
    group_id = fields.Many2one(
        string="Group", comodel_name="github.analysis.rule.group", required=True
    )
    """
    Example paths: https://git-scm.com/docs/gitignore#_pattern_format
    """
    paths = fields.Text(
        help="Define with pathspec especification",
        default="*",
        required=True,
    )

    def _set_spec(self, lines):
        return pathspec.PathSpec.from_lines("gitignore", lines)

    def _get_matches(self, path):
        """
        Get all matches from rule paths (multiple per line allow in rule)
        in a local path
        """
        patterns = self.paths.splitlines()
        patterns = [p.strip() for p in patterns if p.strip()]  # Clean empty lines
        return self._set_spec(patterns).match_tree_files(path)
