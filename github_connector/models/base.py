# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: David BEAL
# Migrated to version 11.0: Petar Najman (petar.najman@modoolar.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _


GITHUB_MODEL = [
    'res.partner', 'github.organization', 'github.team', 'github.repository']


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def load_views(self, views, options=None):
        res = super(Base, self).load_views(views, options)
        if self._name in GITHUB_MODEL:
            for key, value in res.get('fields_views', dict()).items():
                toolbar = value.get('toolbar', False)
                if toolbar:
                    toolbar['action'].append(
                        self.add_update_from_github_action()
                    )
        return res

    @api.model
    def add_update_from_github_action(self):
        action = self.env.ref(
            'github_connector.action_wizard_update_from_github')
        return {
            'id': action.id,
            'name': _('Update From Github'),
            'res_model': u'wizard.update.from.github',
            'src_model': self._name,
            'type': u'ir.actions.act_window',
            'target': 'new',
        }
