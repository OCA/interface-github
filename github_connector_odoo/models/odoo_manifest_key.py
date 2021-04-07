# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class OdooManifestKey(models.Model):
    _name = "odoo.manifest.key"
    _description = "Odoo Manifest Key"

    name = fields.Char()

    @api.model
    def create_if_not_exist(self, name):
        manifest_key = self.search([("name", "=", name)])
        if not manifest_key:
            manifest_key = self.create({"name": name})
        return manifest_key
