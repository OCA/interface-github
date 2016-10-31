# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Github Connector - Odoo',
    'summary': 'Analyze Odoo Modules Informations from github repositories',
    'version': '8.0.0.0.0',
    'category': 'Custom',
    'author': [
        'Odoo Community Association (OCA)',
        'Sylvain LE GAL',
        'GRAP',
    ],
    'depends': [
        'github_connector',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/function.xml',
        'views/view_reporting.xml',
        'views/action.xml',
        'views/menu.xml',
        'views/view_odoo_license.xml',
        'views/view_odoo_author.xml',
        'views/view_odoo_lib_bin.xml',
        'views/view_odoo_lib_python.xml',
        'views/view_odoo_module.xml',
        'views/view_odoo_module_version.xml',
        'views/view_github_organization.xml',
        'views/view_github_repository.xml',
        'views/view_github_repository_branch.xml',
    ],
    'demo': [
        'demo/github_organization.xml',
    ],
    'installable': True,
}
