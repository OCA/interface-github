# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openupgradelib import openupgrade, openupgrade_90

attachment_fields = {
    "odoo.license": [("image", None)],
    "odoo.module.version": [("image", None)],
    "odoo.module": [("image", None)],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_90.convert_binary_field_to_attachment(env, attachment_fields)
