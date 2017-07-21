# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

try:
    import markdown
except ImportError:
    _logger.debug("Cannot import 'markdown' python library.")


class GithubComment(models.Model):
    _name = 'github.comment'
    _inherit = ['abstract.github.model.author']
    _order = 'github_id'

    _github_type = 'issue'
    _github_login_field = False

    _OPINION_SELECTION = [
        ('neutral', 'Neutral'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    ]

    # Column Section
    issue_id = fields.Many2one(
        comodel_name='github.issue', string='Issue / PR', readonly=True,
        required=True, ondelete='cascade')

    body = fields.Char(string='Body', readonly=True)

    html_body = fields.Html(
        string='HTML Body', readonly=True, compute='_compute_by_body',
        multi='body', store=True)

    opinion = fields.Selection(
        string='Opinion', readonly=True, compute='_compute_by_body',
        multi='body', store=True, selection=_OPINION_SELECTION,
        default='neutral')

    is_bot_comment = fields.Boolean(
        string='Is Bot Comment', related='author_id.is_bot_account',
        store=True)

    # Compute section
    @api.multi
    @api.depends('body')
    def _compute_by_body(self):
        for comment in self:
            if comment.body:
                comment.html_body = markdown.markdown(comment.body)
            if ':-1:' in comment.body:
                comment.opinion = 'disapproved'
            elif ':+1:' in comment.body:
                comment.opinion = 'approved'
            else:
                comment.opinion = 'neutral'

    # Overloadable Section
    def get_odoo_data_from_github(self, data):
        res = super(GithubComment, self).get_odoo_data_from_github(data)
        res.update({'body': data['body']})
        return res
