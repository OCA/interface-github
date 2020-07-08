# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import shutil
from datetime import datetime
from subprocess import check_output

from odoo import _, addons, api, exceptions, fields, models, tools
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    from git import Repo
except ImportError:
    _logger.debug("Cannot import 'git' python library.")


class GithubRepository(models.Model):
    _name = "github.repository.branch"
    _inherit = ["abstract.github.model"]
    _order = "repository_id, sequence_serie"
    _description = "Github Repository Branch"

    _github_type = "repository_branches"
    _github_login_field = False

    _SELECTION_STATE = [
        ("to_download", "To Download"),
        ("to_analyze", "To Analyze"),
        ("analyzed", "Analyzed"),
    ]

    # Column Section
    name = fields.Char(string="Name", readonly=True, index=True)

    size = fields.Integer(string="Size (Byte) ", readonly=True)

    mb_size = fields.Float(
        string="Size (Megabyte)", store=True, compute="_compute_mb_size"
    )

    complete_name = fields.Char(
        string="Complete Name", store=True, compute="_compute_complete_name"
    )

    repository_id = fields.Many2one(
        comodel_name="github.repository",
        string="Repository",
        required=True,
        index=True,
        readonly=True,
        ondelete="cascade",
    )

    organization_id = fields.Many2one(
        comodel_name="github.organization",
        string="Organization",
        related="repository_id.organization_id",
        store=True,
        readonly=True,
    )

    organization_serie_id = fields.Many2one(
        comodel_name="github.organization.serie",
        string="Organization Serie",
        store=True,
        compute="_compute_organization_serie_id",
    )

    sequence_serie = fields.Integer(
        string="Sequence Serie", store=True, related="organization_serie_id.sequence"
    )

    local_path = fields.Char(string="Local Path", compute="_compute_local_path")

    state = fields.Selection(
        string="State", selection=_SELECTION_STATE, default="to_download"
    )

    last_download_date = fields.Datetime(string="Last Download Date")

    last_analyze_date = fields.Datetime(string="Last Analyze Date")

    coverage_url = fields.Char(
        string="Coverage URL", store=True, compute="_compute_coverage"
    )

    ci_url = fields.Char(string="CI URL", store=True, compute="_compute_ci")

    github_url = fields.Char(
        string="Github URL", store=True, compute="_compute_github_url"
    )

    # Init Section
    def __init__(self, pool, cr):
        source_path = tools.config.get("source_code_local_path", False)
        if not os.path.exists(source_path):
            try:
                os.makedirs(source_path)
            except Exception as e:
                _logger.error(
                    _(
                        "Error when trying to create the main folder %s\n"
                        " Please check Odoo Access Rights.\n %s"
                    ),
                    source_path,
                    e,
                )
        if source_path and source_path not in addons.__path__:
            addons.__path__.append(source_path)
        super().__init__(pool, cr)

    # Action Section
    def button_download_code(self):
        return self._download_code()

    def button_analyze_code(self):
        return self._analyze_code()

    @api.model
    def cron_download_all(self):
        branches = self.search([])
        branches._download_code()
        return True

    @api.model
    def cron_analyze_all(self):
        branches = self.search([("state", "=", "to_analyze")])
        branches._analyze_code()
        return True

    # Custom
    def create_or_update_from_name(self, repository_id, name):
        branch = self.search(
            [("name", "=", name), ("repository_id", "=", repository_id)]
        )
        if not branch:
            branch = self.create({"name": name, "repository_id": repository_id})
        return branch

    def _download_code(self):
        client = self.get_github_connector("")
        for branch in self:
            if not os.path.exists(branch.local_path):
                _logger.info("Cloning new repository into %s ..." % branch.local_path)
                # Cloning the repository
                try:
                    os.makedirs(branch.local_path)
                except Exception:
                    raise exceptions.Warning(
                        _(
                            "Error when trying to create the folder %s\n"
                            " Please check Odoo Access Rights."
                        )
                        % (branch.local_path)
                    )

                command = ("git clone %s%s/%s.git -b %s %s") % (
                    client.get_http_url(),
                    branch.repository_id.organization_id.github_login,
                    branch.repository_id.name,
                    branch.name,
                    branch.local_path,
                )
                os.system(command)
                branch.write(
                    {"last_download_date": datetime.today(), "state": "to_analyze"}
                )
            else:
                # Update repository
                _logger.info("Pulling existing repository %s ..." % branch.local_path)
                try:
                    res = check_output(
                        ["git", "pull", "origin", branch.name], cwd=branch.local_path
                    )
                    if branch.state == "to_download" or b"up-to-date" not in res:
                        branch.write(
                            {
                                "last_download_date": datetime.today(),
                                "state": "to_analyze",
                            }
                        )
                    else:
                        branch.write({"last_download_date": datetime.today()})
                except Exception:
                    # Trying to clean the local folder
                    _logger.warning(
                        _(
                            "Error when updating the branch %s in the local folder"
                            " %s.\n Deleting the local folder and trying"
                            " again."
                        ),
                        branch.name,
                        branch.local_path,
                    )
                    try:
                        shutil.rmtree(branch.local_path)
                    except Exception:
                        _logger.error(
                            "Error deleting the branch %s in the local folder "
                            "%s. You need to check manually what is happening "
                            "there."
                        )
                    else:
                        branch._download_code()
        return True

    def _get_analyzable_files(self, existing_folder):
        res = []
        for root, _dirs, files in os.walk(existing_folder):
            if "/.git" not in root:
                for fic in files:
                    if fic != ".gitignore":
                        res.append(os.path.join(root, fic))
        return res

    def analyze_code_one(self):
        """Overload Me in custom Module that manage Source Code analysis.
        """
        self.ensure_one()
        path = self.local_path
        # Compute Files Sizes
        size = 0
        for file_path in self._get_analyzable_files(path):
            try:
                size += os.path.getsize(file_path)
            except Exception:
                _logger.warning("Warning : unable to eval the size of '%s'.", file_path)

        try:
            Repo(path)
        except Exception:
            # If it's not a correct repository, we flag the branch
            # to be downloaded again
            self.state = "to_download"
            return {"size": 0}

        return {"size": size}

    def _analyze_code(self):
        partial_commit = safe_eval(
            self.sudo()
            .env["ir.config_parameter"]
            .get_param("git.partial_commit_during_analysis")
        )
        for branch in self:
            path = branch.local_path
            if not os.path.exists(path):
                _logger.warning("Warning Folder %s not found: Analysis skipped.", path)
            else:
                _logger.info("Analyzing Source Code in %s ...", path)
                try:
                    vals = branch.analyze_code_one()
                    vals.update(
                        {"last_analyze_date": datetime.today(), "state": "analyzed"}
                    )
                    # Mark the branch as analyzed
                    branch.write(vals)
                    if partial_commit:
                        self._cr.commit()  # pylint: disable=invalid-commit

                except Exception as e:
                    _logger.warning(
                        "Cannot analyze branch %s so skipping it, error " "is: %s",
                        branch.name,
                        e,
                    )
        return True

    # Compute Section
    @api.depends("name", "repository_id.name")
    def _compute_complete_name(self):
        for branch in self:
            branch.complete_name = (
                branch.repository_id.name + "/" + branch.name
            )

    @api.depends("size")
    def _compute_mb_size(self):
        for branch in self:
            branch.mb_size = float(branch.size) / (1024 ** 2)

    @api.depends("organization_id", "name")
    def _compute_organization_serie_id(self):
        for branch in self:
            for serie in branch.organization_id.organization_serie_ids:
                if serie.name == branch.name:
                    branch.organization_serie_id = serie

    @api.depends("complete_name")
    def _compute_local_path(self):
        source_path = tools.config.get("source_code_local_path", False)
        if not source_path:
            raise exceptions.Warning(
                _(
                    "source_code_local_path should be defined in your "
                    " configuration file"
                )
            )
        for branch in self:
            branch.local_path = os.path.join(
                source_path, branch.organization_id.github_login, branch.complete_name
            )

    @api.depends(
        "name",
        "repository_id.name",
        "organization_id.github_login",
        "organization_id.coverage_url_pattern",
    )
    def _compute_coverage(self):
        for branch in self:
            if not branch.organization_id.coverage_url_pattern:
                branch.coverage_url = ""
            else:
                # This is done because if not, black format the line in a wrong
                # way
                org_id = branch.organization_id
                branch.coverage_url = org_id.coverage_url_pattern.format(
                    organization_name=org_id.github_login,
                    repository_name=branch.repository_id.name,
                    branch_name=branch.name,
                )

    @api.depends(
        "name",
        "repository_id.name",
        "organization_id.github_login",
        "organization_id.ci_url_pattern",
    )
    def _compute_ci(self):
        for branch in self:
            if not branch.organization_id.ci_url_pattern:
                branch.ci_url = ""
                continue
            branch.ci_url = branch.organization_id.ci_url_pattern.format(
                organization_name=branch.organization_id.github_login,
                repository_name=branch.repository_id.name,
                branch_name=branch.name,
            )

    @api.depends("name", "repository_id.complete_name")
    def _compute_github_url(self):
        for branch in self:
            branch.github_url = "https://github.com/{}/{}/tree/{}".format(
                branch.organization_id.github_login,
                branch.repository_id.name,
                branch.name,
            )
