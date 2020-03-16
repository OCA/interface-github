# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from odoo import _, exceptions

_logger = logging.getLogger(__name__)

_MAX_NUMBER_REQUEST = 30

_BASE_URL = "https://api.github.com/"

_GITHUB_URL = "https://github.com/"

_GITHUB_TYPE = [
    ("organization", "Organization"),
    ("repository", "Repository"),
    ("user", "User"),
]

_GITHUB_TYPE_URL = {
    "organization": {"url_get_by_name": "orgs/%s",},
    "user": {"url_get_by_id": "user/%s", "url_get_by_name": "users/%s",},
    "repository": {
        "url_get_by_id": "repositories/%s",
        "url_get_by_name": "repos/%s",
        "url_create": "orgs/%s/repos",
    },
    "team": {"url_get_by_id": "teams/%s", "url_create": "orgs/%s/teams",},
    "organization_members": {"url_get_by_name": "orgs/%s/members",},
    "organization_repositories": {"url_get_by_name": "orgs/%s/repos",},
    "organization_teams": {"url_get_by_name": "orgs/%s/teams",},
    "team_members_member": {"url_get_by_name": "teams/%s/members?role=member",},
    "team_members_maintainer": {"url_get_by_name": "teams/%s/members?role=maintainer",},
    "team_repositories": {"url_get_by_name": "teams/%s/repos",},
    "repository_branches": {"url_get_by_name": "repos/%s/branches",},
}

_CODE_401 = 401
_CODE_403 = 403
_CODE_422 = 422
_CODE_200 = 200
_CODE_201 = 201


class Github(object):
    def __init__(self, github_type, login, password, max_try, token=""):
        super(Github, self).__init__()
        self.github_type = github_type
        self.login = login
        self.password = password
        self.max_try = max_try
        self.token = token

    def _build_url(self, arguments, url_type, page):
        arguments = arguments and arguments or {}
        url = _GITHUB_TYPE_URL[self.github_type][url_type]
        if self.github_type not in _GITHUB_TYPE_URL.keys():
            raise exceptions.Warning(_("'%s' is not implemented.") % self.github_type)
        complete_url = _BASE_URL + url % tuple(arguments)

        if page:
            complete_url += (
                "?" in complete_url and "&" or "?"
            ) + "per_page=%d&page=%d" % (_MAX_NUMBER_REQUEST, page)
        return complete_url

    def get_http_url(self):
        """ Returns the http url to github with the identifications

        :rtype: string
        """
        identification = (
            self.token if self.token else ":".join([self.login, self.password])
        )
        return "https://{}@github.com/".format(identification)

    def list(self, arguments):
        page = 1
        datas = []
        while True:
            pending_datas = self.get(arguments, False, page)
            datas += pending_datas
            if pending_datas == [] or len(pending_datas) < _MAX_NUMBER_REQUEST:
                break
            page += 1
        return datas

    def get_by_url(self, url, call_type, data=False):
        _logger.info("Calling %s" % url)
        for i in range(self.max_try):
            try:
                request_func = self.get_request_function(call_type)
                response = request_func(url, data)
                break
            except Exception as err:
                _logger.warning(
                    "URL Call Error. %d/%d. URL: %s", i, self.max_try, err.__str__(),
                )
        else:
            raise exceptions.Warning(_("Maximum attempts reached."))

        # display an anonymize token or the login
        login = (
            self.token and "* * * * * * * * {}".format(self.token[-4:]) or self.login
        )
        if response.status_code == _CODE_401:
            raise exceptions.Warning(
                _(
                    "401 - Unable to authenticate to Github with the login '%s'.\n"
                    "You should check your credentials in the Odoo"
                    " configuration file."
                )
                % login
            )
        if response.status_code == _CODE_403:
            raise exceptions.Warning(
                _(
                    "Unable to realize the current operation. The login '%s'"
                    " does not have the correct access rights."
                )
                % login
            )
        if response.status_code == _CODE_422:
            raise exceptions.Warning(
                _(
                    "Unable to realize the current operation. Possible reasons:\n"
                    " * You try to create a duplicated item\n"
                    " * Some of the arguments are incorrect"
                )
            )
        elif response.status_code not in [_CODE_200, _CODE_201]:
            raise exceptions.Warning(
                _("The call to '%s' failed:\n" "- Status Code: %d\n" "- Reason: %s")
                % (response.url, response.status_code, response.reason)
            )
        return response.json()

    def get_request_function(self, call_type):
        """ Return the request function to use depending on the call_type and the
        identification type.


        :param str call_type: CRUD method. Can be get or post.
        :rtype: callable
        """
        supported_crud_methods = ("get", "post")
        msg = "`{}` is not a supported CRUD method. Use one of the following {}".format(
            call_type, supported_crud_methods
        )
        assert call_type in supported_crud_methods, msg
        # We want the same signature for all the functions returned to ease the usage.
        # The caller should not have to # consider cases. Cases are handled here.

        if self.token:
            # When an access token is used, the token has to be passed using a headers.
            # there is no Auth class included in requests.
            headers = {"Authorization": "token {}".format(self.token)}

            def get(u, _):
                return requests.get(u, headers=headers)

            def post(u, d):
                json_data = json.dumps(d)
                return requests.get(u, headers=headers, data=json_data)

        else:
            auth = HTTPBasicAuth(self.login, self.password)

            def get(u, _):
                return requests.get(u, auth=auth)

            def post(u, d):
                json_data = json.dumps(d)
                return requests.get(u, auth=auth, data=json_data)

        if call_type == "get":
            return get

        return post

    def get(self, arguments, by_id=False, page=None):
        url = self._build_url(
            arguments, by_id and "url_get_by_id" or "url_get_by_name", page
        )
        return self.get_by_url(url, "get")

    def create(self, arguments, data):
        # pylint: disable=method-required-super
        url = self._build_url(arguments, "url_create", None)
        res = self.get_by_url(url, "post", data)
        return res
