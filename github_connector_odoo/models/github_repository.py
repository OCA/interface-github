# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from urllib.request import Request, urlopen
from collections import defaultdict

from odoo import api, fields, models


class GithubRepository(models.Model):
    _inherit = 'github.repository'

    runbot_id_external = fields.Integer(
        string='ID For Runbot', readonly=True, store=True,
        compute='_compute_runbot_id_external',
        oldname='ci_id_external')

    # Compute Section
    @api.multi
    @api.depends('organization_id.runbot_parse_url')
    def _compute_runbot_id_external(self):
        url_done = defaultdict(list)
        for repository in self:
            url_done[repository.organization_id].append(repository)

        for organization_id, repositories in url_done.items():
            if organization_id.runbot_parse_url:
                runbot_list = urlopen(
                    Request(
                        organization_id.runbot_parse_url)).read().split('\n')
                for item in runbot_list:
                    for repository in repositories:
                        if item.endswith(repository.complete_name):
                            repository.runbot_id_external = item.split('|')[0]
