# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import urllib2
from collections import defaultdict

from openerp import models, fields, api


class GithubRepository(models.Model):
    _inherit = 'github.repository'

    ci_id = fields.Integer(
        string='ID For CI', readonly=True, compute='_compute_ci_id',
        store=True)

    # Compute Section
    @api.multi
    @api.depends('organization_id.ci_url')
    def _compute_ci_id(self):
        url_done = defaultdict(list)
        for repository in self:
            url_done[repository.organization_id].append(repository)

        for organization_id, repositories in url_done.iteritems():
            ci_list = urllib2.urlopen(
                urllib2.Request(organization_id.ci_url)).read().split('\n')
            for item in ci_list:
                for repository in repositories:
                    if item.endswith(repository.complete_name):
                        repository.ci_id = item.split('|')[0]
