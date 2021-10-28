# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

field_renames = [
    ("res.partner", "res_partner", "github_team_ids", "github_team_partner_ids"),
    ("res.partner", "res_partner", "github_login", "github_name"),
    ("github.organization", "github_organization", "github_login", "github_name"),
    (
        "github.repository.branch",
        "github_repository_branch",
        "github_login",
        "github_name",
    ),
    ("github.repository", "github_repository", "github_login", "github_name"),
    ("github.team.partner", "github_team_partner", "github_login", "github_name"),
    ("github.team", "github_team", "github_login", "github_name"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
