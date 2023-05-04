# Copyright Cetmix OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "GitHub Connector Branch options",
    "summary": "Adds extra options for branches/series",
    "version": "14.0.1.0.0",
    "category": "Connector",
    "website": "https://github.com/OCA/interface-github",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "github_connector",
    ],
    "data": [
        "views/view_github_organization.xml",
    ],
}
