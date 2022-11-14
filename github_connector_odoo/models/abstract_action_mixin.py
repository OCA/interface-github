# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AbstractActionMixin(models.AbstractModel):
    _name = "abstract.action.mixin"
    _description = "Abstract Action Mixin"

    def action_open(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "github_connector_odoo.%s" % self._context.get("xml_id")
        )
        action["context"] = dict(self.env.context)
        action["context"].pop("group_by", None)
        action["context"]["search_default_" + self._context.get("field_name")] = self.id
        return action
