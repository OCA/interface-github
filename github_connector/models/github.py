# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import exceptions, _

from requests.auth import HTTPBasicAuth
import requests
import json
import logging

_logger = logging.getLogger(__name__)

_MAX_NUMBER_REQUEST = 30

_BASE_URL = 'https://api.github.com/'

_GITHUB_URL = 'https://github.com/'

_GITHUB_TYPE = [
    ('organization', 'Organization'),
    ('repository', 'Repository'),
    ('user', 'User'),
]

_GITHUB_TYPE_URL = {
    'organization': {'url': 'orgs/%s'},
    'user': {'url': 'users/%s', 'url_by_id': 'user/%s'},
    'repository': {'url': 'repos/%s', 'url_by_id': 'repositories/%s'},
    'team': {'url_by_id': 'teams/%s'},
    'issue': {'url': 'repos/%s/issues/%s'},
    'organization_members': {'url': 'orgs/%s/members'},
    'organization_repositories': {'url': 'orgs/%s/repos'},
    'organization_teams': {'url': 'orgs/%s/teams'},
    'team_members': {'url': 'teams/%s/members'},
    'repository_issues': {'url': 'repos/%s/issues?state=all'},
    'issue_comments': {'url': 'repos/%s/issues/%s/comments'},
    'repository_branches': {'url': 'repos/%s/branches'},
}


class Github(object):

    def __init__(self, github_type, login, password, max_try):
        super(Github, self).__init__()
        self.github_type = github_type
        self.login = login
        self.password = password
        self.max_try = max_try

    def list(self, arguments):
        page = 1
        datas = []
        while True:
            pending_datas = self.get(arguments, False, page)
            datas += pending_datas
            if pending_datas == [] or\
                    len(pending_datas) < _MAX_NUMBER_REQUEST:
                break
            page += 1
        return datas

    def get_by_url(self, url):
        _logger.info("Calling %s" % (url))
        for i in range(self.max_try):
            try:
                response = requests.get(
                    url, auth=HTTPBasicAuth(self.login, self.password))
                break
            except Exception as err:
                _logger.warning("URL Call Error. %d/%d. URL: %s" % (
                    i, self.max_try, err.__str__()))
        else:
            raise err

        if response.status_code == 401:
            raise exceptions.Warning(
                _("Github Access Error"),
                _("Unable to authenticate to Github with the login '%s'.\n"
                    "You should Check your credentials in the Odoo"
                    " configuration file.") % (self.login))
        elif response.status_code != 200:
            raise exceptions.Warning(
                _("Github Error"),
                _("The call to '%s' failed:\n"
                    "- Status Code: %d\n"
                    "- Reason: %s") % (
                    response.url, response.status_code, response.reason))
        return json.loads(response.content)

    def get(self, arguments, by_id=False, page=None):
        url = self._build_url(arguments, by_id, page)
        return self.get_by_url(url)

    def _build_url(self, arguments, by_id, page):
        if by_id:
            url = _GITHUB_TYPE_URL[self.github_type]['url_by_id']
        else:
            url = _GITHUB_TYPE_URL[self.github_type]['url']
        if self.github_type not in _GITHUB_TYPE_URL.keys():
            raise exceptions.Warning(
                _("Unimplemented Connection"),
                _("'%s' is not implemented.") % (self.github_type))
        complete_url = _BASE_URL + url % tuple(arguments)

        if page:
            complete_url += ('?' in complete_url and '&' or '?') +\
                'per_page=%d&page=%d' % (_MAX_NUMBER_REQUEST, page)
        return complete_url
