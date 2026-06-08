# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VcpComment(models.Model):
    _inherit = "vcp.comment"

    # /!\ Be carefull here
    # Natively the vcp module do not know the organization of the contributor
    # So in the VCP module the "partner organization" is the "partner organization"
    # that have open the PR.
    # Here we change the behaviour to use the "partner organization" of the contributor
    partner_organization_id = fields.Many2one(
        "res.partner",
        related=False,
        store=True,
        compute="_compute_partner_organization_id",
        help="The organization related to the user that have done the comment",
    )

    @api.depends(
        "user_id.partner_id.commercial_partner_id",
        "user_id.partner_id.organization_history_ids.date_start",
        "user_id.partner_id.organization_history_ids.partner_organization_id",
        "created_at",
    )
    def _compute_partner_organization_id(self):
        for record in self:
            record.partner_organization_id = (
                record.user_id.partner_id._get_organization(record.created_at.date())
            )
