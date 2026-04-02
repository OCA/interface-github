from odoo import api, models


class BasePartnerMergeAutomaticWizard(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    @api.model
    def _update_values(self, src_partners, dst_partner):
        # Preserve github_name from source partners before clearing it to
        # avoid unique constraint violation during merge.
        github_name = dst_partner.github_name
        if not github_name:
            for partner in src_partners:
                if partner.github_name:
                    github_name = partner.github_name
                    break
        src_partners.sudo().write({'github_name': False})
        result = super()._update_values(src_partners, dst_partner)
        if github_name and not dst_partner.github_name:
            dst_partner.sudo().write({'github_name': github_name})
        return result
