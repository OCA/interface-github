# Copyright 2018 Road-Support - Roel Adriaans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

_OWNER_TYPE_SELECTION = [
    ('undefined', 'Undefined'),
    ('editor', 'Odoo Editor'),
    ('oca', 'OCA'),
    ('extra', 'Extra'),
    ('custom', 'Custom'),
]

class GithubOrganization(models.Model):
    _inherit = 'github.organization'

    owner_type = fields.Selection(
        string='Owner Type', selection=_OWNER_TYPE_SELECTION,
        required=True, default='custom')

    # TODO make a constraint to forbid undefined value
