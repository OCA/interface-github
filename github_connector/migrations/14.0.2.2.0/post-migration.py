#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    branches = env["github.repository.branch"].search([])
    repositories = branches.repository_id
    repositories.modified(
        [
            "complete_name",
        ]
    )
    branches.recompute(
        fnames=[
            "complete_name",
        ],
    )
