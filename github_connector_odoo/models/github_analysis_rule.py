# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class GithubAnalysisRule(models.Model):
    _inherit = "github.analysis.rule"

    has_odoo_addons = fields.Boolean(string="Has odoo addons?")
    manifest_key_ids = fields.Many2many(
        comodel_name="odoo.manifest.key", string="Manifest keys"
    )

    def _get_matches(self, path):
        """
        Override according to has_odoo_addons rules
        """
        if self.has_odoo_addons:
            spec = self._set_spec(["*"])
            file_paths = []
            for path_item in spec.match_tree(path):
                file_paths.append(f"{path}/{path_item}")
            spec = self._set_spec(self.paths.splitlines())
            return spec.match_files(file_paths)
        return super()._get_matches(path)
