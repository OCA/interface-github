# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Migrated to version 11.0: Petar Najman (petar.najman@modoolar.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class GithubTeamRepository(models.Model):
    _name = 'github.team.repository'
    _order = 'team_id, repository_id'
    _rec_name = 'repository_id'

    _PERMISSION_SELECTION = [
        ('undefined', 'Undefined'),
        ('read', 'Read'),
        ('write', 'Write'),
        ('admin', 'Admin'),
    ]

    # Column Section
    team_id = fields.Many2one(
        comodel_name='github.team', string='Team',
        required=True, index=True, readonly=True, ondelete='cascade')

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository',
        required=True, index=True, readonly=True, ondelete='cascade')

    permission = fields.Selection(
        selection=_PERMISSION_SELECTION, string='Permission', required=True,
        readonly=True)
