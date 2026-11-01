# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def write(self, vals):
        # Override to synchronize existing membership lines with the invoice
        # line, as native code only creates them and ignores later changes.
        res = super().write(vals)

        to_process = self.filtered(
            lambda line: line.move_id.move_type == "out_invoice"
            and line.product_id.membership
        )
        if not to_process:
            return res

        existing_memberships = self.env["membership.membership_line"].search(
            [("account_invoice_line", "in", to_process.ids)]
        )
        for membership in existing_memberships:
            invoice_line = membership.account_invoice_line
            date_from = invoice_line.product_id.membership_date_from
            date_to = invoice_line.product_id.membership_date_to
            if date_from and date_from < (
                invoice_line.move_id.invoice_date or date.min
            ) < (date_to or date.min):
                date_from = invoice_line.move_id.invoice_date
            product = invoice_line.product_id
            if product.membership and product.membership_type == "variable":
                vals = invoice_line._prepare_membership_line(
                    invoice_line.move_id,
                    invoice_line.product_id,
                    invoice_line.price_unit,
                    invoice_line.id,
                    qty=invoice_line.quantity,
                )
                # We refresh existing membership lines on every invoice
                # line write: never reset the status there. It is handled by
                # membership_extension (action_post / button_draft / button_cancel)
                # and recomputed from the invoice payment state.
                vals.pop("state", None)
            else:
                vals = {
                    "partner": invoice_line.move_id.partner_id.id,
                    "membership_id": invoice_line.product_id.id,
                    "member_price": invoice_line.price_unit,
                    "date": fields.Date.today(),
                    "date_from": date_from,
                    "date_to": date_to,
                }
            membership.write(
                {
                    "partner": invoice_line.move_id.partner_id.id,
                    "membership_id": invoice_line.product_id.id,
                    "member_price": invoice_line.price_unit,
                    "date": fields.Date.today(),
                    "date_from": date_from,
                    "date_to": date_to,
                }
            )
        return res
