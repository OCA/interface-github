# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, _
UNIQUE_ID_MODEL = (
    1121141111061019911695109111100112349951161119511226115107)

UNIQUE_ID_MODEL_AUTHOR = (
    1121112322221101991169510911110011234995949400560026115107)


GITHUB_MODEL = [
    'res.partner', 'github.organization', 'github.team', 'github.repository',
    'github.issue', 'github.comment']

GITHUB_MODEL_AUTHOR = ['github.issue', 'github.comment']


class IrValues(models.Model):
    _inherit = 'ir.values'

    @api.model
    def get_actions(self, action_slot, model, res_id=False):
        """ Add an action to all models that inherit of abstract.github.model
        """
        res = super(IrValues, self).get_actions(
            action_slot, model, res_id=res_id)
        if action_slot == 'client_action_multi' and model in GITHUB_MODEL:
            action = self.add_update_from_github_action(model, res_id=res_id)
            value = (UNIQUE_ID_MODEL, 'github_connector', action)
            res.insert(0, value)

        if action_slot == 'client_action_multi'\
                and model in GITHUB_MODEL_AUTHOR:
            action = self.add_update_company_author_action(
                model, res_id=res_id)
            value = (UNIQUE_ID_MODEL_AUTHOR, 'github_connector', action)
            res.insert(0, value)
        return res

    @api.model
    def add_update_from_github_action(self, model, res_id=False):
        action = self.env.ref(
            'github_connector.action_wizard_update_from_github')
        return {
            'id': action.id,
            'name': _('Update From Github'),
            'res_model': u'wizard.update.from.github',
            'src_model': model,
            'type': u'ir.actions.act_window',
            'target': 'new',
        }

    @api.model
    def add_update_company_author_action(self, model, res_id=False):
        action = self.env.ref(
            'github_connector.action_wizard_update_company_author')
        return {
            'id': action.id,
            'name': _('Update Company Author'),
            'res_model': u'wizard.update.company.author',
            'src_model': model,
            'type': u'ir.actions.act_window',
            'target': 'new',
        }
