# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

column_renames = {
    "res_partner": [
        ("github_team_ids", "github_team_partner_ids"),
        ("github_login", "github_name"),
    ],
    "github_organization": [
        ("github_login", "github_name"),
    ],
    "github_repository_branch": [
        ("github_login", "github_name"),
    ],
    "github_repository": [
        ("github_login", "github_name"),
    ],
    "github_team_partner": [
        ("github_login", "github_name"),
    ],
    "github_team": [
        ("github_login", "github_name"),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
