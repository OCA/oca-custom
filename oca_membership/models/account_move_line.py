# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_membership_line_data(self):
        self.ensure_one()
        # In the OCA instance we use a patch on native membership module :
        # https://github.com/Therp/OCB/pull/2
        # So we need to adapt the variable membership to this patch.
        # This can be removed in v19.0 because the patch has been applied in the main
        # membership module
        if self.product_id.membership and self.product_id.membership_type == "variable":
            return self._prepare_membership_line(
                self.move_id,
                self.product_id,
                self.price_unit,
                self.id,
                qty=self.quantity,
            )
        return super()._prepare_membership_line_data()
