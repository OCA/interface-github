#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Github Connector - Pull Requests",
    "summary": "Manage Pull Requests",
    "website": "https://github.com/OCA/interface-github",
    "category": "Connector",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "author": "Aion Tech, Odoo Community Association (OCA)",
    "depends": [
        "github_connector",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/github_pull_request_views.xml",
        "views/github_repository_views.xml",
        "data/ir_cron_data.xml",
    ],
}
