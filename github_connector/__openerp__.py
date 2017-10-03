# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Github Connector',
    'summary': 'Synchronize information from Github repositories',
    'version': '10.0.1.0.0',
    'category': 'Connector',
    'license': 'AGPL-3',
    'author':
        'Odoo Community Association (OCA), GRAP, Akretion'
        ', Sylvain LE GAL',
    'depends': [
        'base',
        'web_kanban',
    ],
    'data': [
        'security/ir_model_category.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'views/view_wizard_load_github_model.xml',
        'views/view_wizard_update_from_github.xml',
        'views/view_wizard_update_branch_list.xml',
        'views/view_reporting.xml',
        'views/view_github_team_partner.xml',
        'views/view_github_team_repository.xml',
        'views/action.xml',
        'views/view_res_partner.xml',
        'views/view_github_organization.xml',
        'views/view_wizard_download_analyze_branch.xml',
        'views/view_github_repository.xml',
        'views/view_github_repository_branch.xml',
        'views/view_github_team.xml',
        'views/menu.xml',
        'views/view_wizard_create_team.xml',
        'views/view_wizard_create_repository.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/github_organization.xml',
        'demo/github_organization_serie.xml',
    ],
    'installable': True,
    'external_dependencies': {
        'python': ['git'],
    },
}
