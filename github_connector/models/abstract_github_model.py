# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from urllib.request import urlopen
import logging

from odoo import _, api, exceptions, fields, models, tools
from odoo.exceptions import UserError

from .github import Github

_logger = logging.getLogger(__name__)


class AbstractGithubModel(models.AbstractModel):
    """
    This abstract model is used to share all features related to github model.
    Note that some fields and function have to be defined in the inherited
    model. (github_type for instance)
    """

    _name = 'abstract.github.model'
    _description = 'Github abstract model'
    _github_type = None
    _github_login_field = None
    _need_individual_call = False
    _field_list_prevent_overwrite = []

    github_id_external = fields.Char(
        string='Github Id', readonly=True, index=True, oldname='github_id')

    github_login = fields.Char(
        string='Github Technical Name', readonly=True, index=True)

    github_url = fields.Char(
        string='Github URL', readonly=True)

    github_create_date = fields.Datetime(
        string='Create Date on Github', readonly=True)

    github_write_date = fields.Datetime(
        string='Last Write Date on Github', readonly=True)

    github_last_sync_date = fields.Datetime(
        string='Last Sync Date with Github', readonly=True)

    # Overloadable Section
    def github_type(self):
        if self._github_type is None:
            raise exceptions.Warning(_(
                "Feature not Implemented : Please define 'github_type'"
                " function in child model."))
        else:
            return self._github_type

    def github_login_field(self):
        if self._github_login_field is None:
            raise exceptions.Warning(_(
                "Feature not Implemented : Please define 'github_login_field'"
                " function in child model."))
        else:
            return self._github_login_field

    @api.model
    def get_conversion_dict(self):
        """
        Prepare function that map Github fields to Odoo fields
        :return: Dictionary {odoo_field: github_field}
        """
        return {
            'github_id_external': 'id',
            'github_url': 'html_url',
            'github_login': self.github_login_field(),
            'github_create_date': 'created_at',
            'github_write_date': 'updated_at',
        }

    @api.model
    def get_odoo_data_from_github(self, data):
        """Prepare function that map Github data to create in Odoo"""
        map_dict = self.get_conversion_dict()
        res = {}
        for k, v in map_dict.items():
            if hasattr(self, k) and data.get(v, False):
                res.update({k: data[v]})
        res.update({'github_last_sync_date': fields.Datetime.now()})
        return res

    @api.multi
    def get_github_data_from_odoo(self):
        """Prepare function that map Odoo data to create in Github.
        Usefull only if your model implement creation in github"""
        self.ensure_one()
        raise exceptions.Warning(_(
            "Feature not Implemented : Please define"
            " 'get_github_data_from_odoo' function in child model."))

    @api.multi
    def get_github_args_for_creation(self):
        """Should Return list of arguments required to create the given item
        in Github.
        Usefull only if your model implement creation in github"""
        self.ensure_one()
        raise exceptions.Warning(_(
            "Feature not Implemented : Please define"
            " 'get_github_args_for_creation' function in child model."))

    @api.multi
    def full_update(self):
        """Override this function in models that inherit this abstract
        to mention which items should be synchronized from github when the
        user click on 'Full Update' Button"""
        pass

    @api.multi
    def _hook_after_github_creation(self):
        """Hook that will be called, after a creation in github.
        Override this function to add custom logic for after creation."""
        pass

    # Custom Public Function
    @api.model
    def get_from_id_or_create(self, data, extra_data=None):
        """Search if the odoo object exists in database. If yes, returns the
            object. Otherwise, creates the new object.

            :param data: dict with github 'id' and 'url' keys
            :return: The searched or created object

            :Example:

            >>> self.env['github_organization'].get_from_id_or_create(
                {'id': 7600578, 'url': 'https://api.github.com/orgs/OCA'})
        """
        extra_data = extra_data and extra_data or {}

        # We try to search object by id
        existing_object = self.search(
            [('github_id_external', '=', data['id'])])
        if existing_object:
            return existing_object

        # We try to see if object exist by name (instead of id)
        if self._github_login_field and self._github_login_field in data:
            existing_object = self.search([
                ('github_login', '=', data[self._github_login_field])])
            if len(existing_object) == 1:
                # Update the existing object with the id
                existing_object.github_id_external = data['id']
                _logger.info(
                    "Existing object %s#%d with Github name '%s' has been"
                    " updated with unique Github id %s#%s",
                    self._name, existing_object.id,
                    data[self._github_login_field], data['id'],
                    self.github_type())
                return existing_object
            elif len(existing_object) > 1:
                raise UserError(
                    _("Duplicate object with Github login %s") %
                    (data[self._github_login_field], ))

        if self._need_individual_call:
            github_connector = self.get_github_connector(self.github_type())
            data = github_connector.get_by_url(data['url'], 'get')
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
        github_connector = self.get_github_connector(self.github_type())
        res = github_connector.get([name])
        # search if ID doesn't exist in database
        current_object = self.search([('github_id_external', '=', res['id'])])
        if not current_object:
            # Create the object
            return self._create_from_github_data(res)
        else:
            return current_object

    @api.multi
    def button_update_from_github_light(self):
        return self.update_from_github(False)

    @api.multi
    def button_update_from_github_full(self):
        return self.update_from_github(True)

    @api.multi
    def update_from_github(self, child_update):
        """Call Github API, using a URL using github id. Load data and
            update Odoo object accordingly, if the odoo object is obsolete.
            (Based on last write dates)

            :param child_update: set to True if you want to reload childs
                Objects linked to this object. (like members for teams)
        """
        github_connector = self.get_github_connector(self.github_type())
        for item in self:
            if item._name == 'github.organization':
                # Github doesn't provides api to load an organization by id
                res = github_connector.get([item.github_login])
            else:
                res = github_connector.get(
                    [item.github_id_external], by_id=True)
            item._update_from_github_data(res)
        if child_update:
            self.full_update()

    def get_base64_image_from_github(self, url):
        max_try = int(
            self.sudo().env['ir.config_parameter'].get_param('github.max_try'))
        for i in range(max_try):
            try:
                stream = urlopen(url).read()
                break
            except Exception as err:
                _logger.warning("URL Call Error. %s" % (err.__str__()))
        else:
            raise exceptions.Warning(_('Maximum attempts reached.'))
        return base64.standard_b64encode(stream)

    # Custom Private Function
    @api.model
    def _create_from_github_data(self, data, extra_data=None):
        extra_data = extra_data and extra_data or {}
        vals = self.get_odoo_data_from_github(data)
        vals.update(extra_data)
        return self.create(vals)

    @api.multi
    def _update_from_github_data(self, data):
        for item in self:
            vals = self.get_odoo_data_from_github(data)
            # Optimization. Due to the fact that github datas rarely change,
            # and that there a lot of related / computed fields invalidation
            # process, we realize a write only if data changed
            to_write = {}
            for k, v in vals.items():
                if hasattr(item[k], 'id'):
                    to_compare = item[k].id
                else:
                    to_compare = item[k]
                # do not overwrite existing values for some given fields
                if to_compare != v and (
                        k not in self._field_list_prevent_overwrite or
                        to_compare is False):
                    to_write[k] = v
            if to_write:
                item.write(to_write)

    @api.multi
    def get_github_connector(self, github_type):
        if (not tools.config.get('github_login') or
                not tools.config.get('github_password')):
            raise exceptions.Warning(_(
                "Please add 'github_login' and 'github_password' "
                "in Odoo configuration file."))
        return Github(
            github_type,
            tools.config['github_login'],
            tools.config['github_password'],
            int(self.sudo().env['ir.config_parameter'].get_param(
                'github.max_try')))

    @api.multi
    def create_in_github(self, model_obj):
        self.ensure_one()
        github_connector = self.get_github_connector(self.github_type())
        # Create in Github
        response = github_connector.create(
            self.get_github_args_for_creation(),
            self.get_github_data_from_odoo())
        # Create in Odoo with the returned data and update object
        new_item = model_obj._create_from_github_data(response)
        new_item.full_update()
        new_item._hook_after_github_creation()
        return new_item

    @api.multi
    def get_action(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
        }
