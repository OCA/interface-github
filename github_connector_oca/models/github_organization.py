# Copyright 2018 Road-Support - Roel Adriaans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)

_OWNER_TYPE_SELECTION = [
    ('1_editor', 'Odoo SA'),
    ('2_oca', 'OCA'),
    ('3_extra', 'Extra'),
    ('4_custom', 'Custom'),
    ('5_undefined', 'Undefined'),
]


class GithubOrganization(models.Model):
    _inherit = 'github.organization'

    owner_type = fields.Selection(
        string='Owner Type', selection=_OWNER_TYPE_SELECTION,
        required=True, default='4_custom')

    # TODO make a constraint to forbid undefined value
