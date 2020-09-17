# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# Copyright 2021 Tecnativa - João Marques
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging
from datetime import datetime
from urllib.request import urlopen

from github import Github
from github.GithubException import UnknownObjectException

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

_GITHUB_URL = "https://github.com/"


class AbstractGithubModel(models.AbstractModel):
    """
    This abstract model is used to share all features related to github model.
    Note that some fields and function have to be defined in the inherited
    model.
    """

    _name = "abstract.github.model"
    _description = "Github abstract model"
    _github_login_field = None
    _need_individual_call = False
    _field_list_prevent_overwrite = []

    github_id_external = fields.Char(string="Github Id", readonly=True, index=True)

    github_name = fields.Char(string="Github Technical Name", readonly=True, index=True)

    github_url = fields.Char(string="Github URL", readonly=True)

    github_create_date = fields.Datetime(string="Create Date on Github", readonly=True)

    github_write_date = fields.Datetime(
        string="Last Write Date on Github", readonly=True
    )

    github_last_sync_date = fields.Datetime(
        string="Last Sync Date with Github", readonly=True
    )

    # Overloadable Section
    def github_login_field(self):
        if self._github_login_field is None:
            raise UserError(
                _(
                    "Feature not Implemented : Please define 'github_login_field'"
                    " function in child model."
                )
            )
        else:
            return self._github_login_field

    @api.model
    def get_conversion_dict(self):
        """
        Prepare function that builds a map from Github fields to Odoo fields

        :return: Dictionary {odoo_field: github_field}
        """
        return {
            "github_id_external": "id",
            "github_url": "html_url",
            "github_name": self.github_login_field(),
            "github_create_date": "created_at",
            "github_write_date": "updated_at",
        }

    def process_timezone_fields(self, res):
        for k, v in res.items():
            if self._fields[k].type == "datetime" and isinstance(v, str):
                res[k] = datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")

    @api.model
    def get_odoo_data_from_github(self, data):
        """Prepare function that maps data from a Github object to a dictionary of
        values ready to create an Odoo record
        """
        map_dict = self.get_conversion_dict()
        res = {}
        for k, v in map_dict.items():
            if hasattr(self, k) and hasattr(data, v):
                res.update({k: getattr(data, v)})
        res.update({"github_last_sync_date": fields.Datetime.now()})
        # res.update({"github_type": type(data).__name__})
        self.process_timezone_fields(res)
        return res

    def get_github_base_obj_for_creation(self):
        """Should return the base object required to create the given item
        in Github.
        Usefull only if your model implements creation in github
        """
        self.ensure_one()
        raise UserError(
            _(
                "Feature not Implemented : Please define"
                " 'get_github_base_obj_for_creation' function in child model."
            )
        )

    def full_update(self):
        """Override this function in models that inherit this abstract
        to mention which items should be synchronized from github when the
        user clicks the 'Full Update' Button"""

    def _hook_after_github_creation(self):
        """Hook that will be called after a creation in github.
        Override this function to add custom logic for after creation."""

    # Custom Public Function
    @api.model
    def get_from_id_or_create(self, gh_data=None, data=None, extra_data=None):
        """Search if an Odoo object related to the Github data exists in database.
        If it does, it returns the object. Otherwise, it creates the new object.

        :param gh_data: Github object the will be used to get/create Odoo record
        :param data: dict with github 'id' and 'url' keys (deprecated)
        :param extra_data: dict with extra data to be put into the Odoo record
        :return: The searched or created object

        :Example:

        >>> self.env['github_organization'].get_from_id_or_create(
            data={'id': 7600578, 'url': 'https://api.github.com/orgs/OCA'})
        """
        extra_data = extra_data or {}
        if gh_data and not data:
            # Get a dictionary of data corresponding to the Github object
            data = self.get_odoo_data_from_github(gh_data)
        # We try to search object by id
        existing_object = None
        if "github_id_external" in data:
            existing_object = self.with_context(active_test=False).search(
                [("github_id_external", "=", data["github_id_external"])]
            )
        if existing_object:
            return existing_object
        # We try to search the object by name (instead of id)
        if self._github_login_field and self._github_login_field in data:
            existing_object = self.with_context(active_test=False).search(
                [("github_name", "=", data[self._github_login_field])]
            )
            if len(existing_object) == 1:
                # Update the existing object
                existing_object.github_id_external = (
                    data["github_id_external"]
                    if "github_id_external" in data
                    else existing_object.find_related_github_object().id
                )
                _logger.info(
                    "Existing object %s#%d with Github name '%s' has been"
                    " updated from a '%s' object with unique Github id %s",
                    self._name,
                    existing_object.id,
                    data[self._github_login_field],
                    type(data).__name__,
                    existing_object.github_id_external,
                )
                return existing_object
            elif len(existing_object) > 1:
                raise UserError(
                    _("Duplicate object with Github login %s")
                    % (data[self._github_login_field],)
                )
        # if self._need_individual_call:
        #     github_connector = self.get_github_connector(self.github_type())
        #     data = github_connector.get_by_url(data["url"], "get")
        # Create a new object otherwise
        # The _create function already parses the Github object to obtain the full
        # Odoo dictionary, so we need to pass the full gh_data object.
        return self._create_from_github_data(data, extra_data)

    @api.model
    def create_from_name(self, name):
        """Call Github API, using a URL using github name. Load data and
        Create Odoo object accordingly, if the odoo object doesn't exist.

        :param name: the github name to load
        :return: The created object

        :Example:

        >>> self.env['github_organization'].create_from_name('OCA')
        >>> self.env['github_repository'].create_from_name('OCA/web')
        """
        gh_api = self.get_github_connector()
        p_name = name.rstrip("/").lstrip(
            "/"
        )  # strip any / in the beggining of end just in case
        try:
            if "/" in p_name:
                # It's a repo
                gh_obj = gh_api.get_repo(p_name)
            else:
                try:
                    # Try to get an organization 1st.
                    # An organization is always an user, but a user is not necessarily an org.
                    gh_obj = gh_api.get_organization(p_name)
                except UnknownObjectException:
                    # Try to get an user.
                    gh_obj = gh_api.get_user(p_name)
        except UnknownObjectException:
            raise UserError(_("Invalid name '%s' provided" % name))
        res = self.get_odoo_data_from_github(gh_obj)
        # search if ID doesn't exist in database
        current_object = self.with_context(active_test=False).search(
            [("github_id_external", "=", res["github_id_external"])]
        )
        if current_object:
            return current_object
        # Create the object
        return self._create_from_github_data(res)

    def button_update_from_github_light(self):
        return self.update_from_github(child_update=False)

    def button_update_from_github_full(self):
        return self.update_from_github(child_update=True)

    @api.model
    def find_related_github_object(self, id=None):
        """Query Github API to find the related object

        This function should be overwritten in the child classes.
        """

    def update_from_github(self, child_update):
        """Call Github API, using a URL using github id. Load data and
        update Odoo object accordingly, if the odoo object is obsolete.
        (Based on last write dates)

        :param child_update: set to True if you want to reload childs
            Objects linked to this object. (like members for teams)
        """
        for item in self:
            gh_obj = item.find_related_github_object()
            data = self.get_odoo_data_from_github(gh_obj)
            item._update_from_github_data(data)
        if child_update:
            self.full_update()

    def get_base64_image_from_github(self, url):
        max_try = int(
            self.sudo().env["ir.config_parameter"].get_param("github.max_try")
        )
        for _i in range(max_try):
            try:
                stream = urlopen(url, timeout=10).read()
                break
            except Exception as err:
                _logger.warning("URL Call Error. %s" % (err.__str__()))
        else:
            raise UserError(_("Maximum attempts reached."))
        return base64.standard_b64encode(stream)

    # Custom Private Function
    @api.model
    def _create_from_github_data(self, data, extra_data=None):
        extra_data = extra_data and extra_data or {}
        data.update(extra_data)
        return self.create(data)

    def _update_from_github_data(self, data):
        for item in self:
            # Optimization. Due to the fact that github datas rarely change,
            # and that there a lot of related / computed fields invalidation
            # process, we realize a write only if data changed
            to_write = {}
            for k, v in data.items():
                if hasattr(item[k], "id"):
                    to_compare = item[k].id
                else:
                    to_compare = item[k]
                # do not overwrite existing values for some given fields
                if to_compare != v and (
                    k not in self._field_list_prevent_overwrite or to_compare is False
                ):
                    to_write[k] = v
            if to_write:
                item.write(to_write)

    def get_github_connector(self):
        ICP = self.env["ir.config_parameter"]
        token = tools.config.get("github_token") or ICP.get_param(
            "github.access_token", default=""
        )
        if not token:
            raise UserError(
                _(
                    "Please add the 'github_token' in Odoo configuration file"
                    " or as the 'github.access_token' configuration parameter."
                )
            )
        return Github(token)

    def create_in_github(self):
        """Create an object in Github through the API

        As this depends on each object, it should be overwritten in each
        implementation class
        """

    def get_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "view_mode": "form",
            "res_model": self._name,
            "res_id": self.id,
        }
