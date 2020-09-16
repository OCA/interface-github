# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pathspec
from pygount import SourceAnalysis

from odoo import fields, models


class GithubAnalysisRule(models.Model):
    _name = "github.analysis.rule"
    _description = "Github Analysis Rule"

    name = fields.Char(string="Name", required=True)
    group_id = fields.Many2one(
        string="Group", comodel_name="github.analysis.rule.group", required=True
    )
    """
    Example paths: https://git-scm.com/docs/gitignore#_pattern_format
    """
    paths = fields.Text(
        string="Paths",
        help="Define with pathspec especification",
        default="*",
        required=True,
    )

    def _get_matches(self, path):
        """
        Get all matches from rule paths (multiple per line allow in rule)
        in a local path
        """
        spec = pathspec.PathSpec.from_lines("gitwildmatch", self.paths.splitlines())
        return spec.match_tree(path)

    def _analysis_file(self, path):
        file_res = SourceAnalysis.from_file(path, "")
        return {
            "path": file_res._path,
            "language": file_res._language,
            "code": file_res._code,
            "documentation": file_res._documentation,
            "empty": file_res._empty,
            "string": file_res._string,
        }
