# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_membership_invoice = fields.Boolean(
        compute="_compute_is_membership_invoice",
        search="_search_is_membership_invoice",
    )

    @api.depends("line_ids.product_id.membership")
    def _compute_is_membership_invoice(self):
        for move in self:
            move.is_membership_invoice = any(
                move.line_ids.product_id.mapped("membership")
            )

    def _search_is_membership_invoice(self, operator, value):
        return [("line_ids.product_id.membership", operator, value)]
