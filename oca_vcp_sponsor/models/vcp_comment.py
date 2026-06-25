# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models


class VcpComment(models.Model):
    _inherit = "vcp.comment"

    @api.depends(
        "user_id.partner_id.commercial_partner_id.sponsor_parent_id",
        "user_id.partner_id.organization_history_ids.partner_organization_id.sponsor_parent_id",
    )
    def _compute_partner_organization_id(self):
        return super()._compute_partner_organization_id()
