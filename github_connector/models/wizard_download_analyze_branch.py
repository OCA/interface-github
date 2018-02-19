# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Migrated to version 11.0: Petar Najman (petar.najman@modoolar.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class WizardDownloadAnalyzeBranch(models.TransientModel):
    _name = 'wizard.download.analyze.branch'

    download_source_code = fields.Boolean(
        string='Download Source Code', default=True)

    analyze_source_code = fields.Boolean(
        string='Analyze Source Code', default=True)

    @api.multi
    def apply(self):
        repository_obj = self.env['github.repository.branch']
        for wizard in self:
            branches = repository_obj.browse(self._context['active_ids'])
            if wizard.download_source_code:
                branches.button_download_code()
            if wizard.analyze_source_code:
                branches.button_analyze_code()
