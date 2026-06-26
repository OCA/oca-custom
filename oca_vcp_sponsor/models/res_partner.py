# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends(
        "commercial_partner_id.sponsor_parent_id",
        "organization_history_ids.partner_id.sponsor_parent_id",
    )
    def _compute_current_organization_id(self):
        return super()._compute_current_organization_id()

    def _get_organization(self, date=None):
        partner = super()._get_organization(date)
        return partner.sponsor_parent_id or partner
