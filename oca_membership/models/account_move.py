# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_membership_invoice = fields.Boolean(
        compute="_compute_is_membership_invoice",
        store=True,
    )

    @api.depends("line_ids.product_id.membership")
    def _compute_is_membership_invoice(self):
        for move in self:
            move.is_membership_invoice = any(
                move.line_ids.product_id.mapped("membership")
            )
