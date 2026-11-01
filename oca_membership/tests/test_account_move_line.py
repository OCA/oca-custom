# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests import Form, tagged

from odoo.addons.membership.tests.common import TestMembershipCommon


@tagged("post_install", "-at_install")
class TestAccountMoveLineMembership(TestMembershipCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Membership product sold first, with an already elapsed date window
        cls.membership_old = cls.env["product.product"].create(
            {
                "membership": True,
                "membership_date_from": datetime.date.today()
                + relativedelta(months=-1),
                "membership_date_to": datetime.date.today() + relativedelta(days=-2),
                "name": "Membership Old",
                "type": "service",
                "list_price": 90.00,
            }
        )
        # Membership product the invoice line is switched to
        cls.membership_new = cls.env["product.product"].create(
            {
                "membership": True,
                "membership_date_from": datetime.date.today() + relativedelta(days=-2),
                "membership_date_to": datetime.date.today() + relativedelta(months=1),
                "name": "Membership New",
                "type": "service",
                "list_price": 100.00,
            }
        )

    def test_change_membership_on_account_move_line(self):
        invoice = self.partner_1.create_membership_invoice(
            self.membership_old,
            self.membership_old.list_price,
        )
        with Form(invoice) as invoice_form:
            line_form = invoice_form.invoice_line_ids.edit(0)
            line_form.product_id = self.membership_new
            line_form.save()

        invoice_line = invoice.invoice_line_ids[0]
        self.assertEqual(
            invoice_line.price_unit,
            self.membership_new.list_price,
        )

        membership_lines = self.env["membership.membership_line"].search(
            [("account_invoice_line", "=", invoice_line.id)]
        )
        self.assertEqual(len(membership_lines), 1)
        membership_line = membership_lines[0]
        self.assertEqual(
            membership_line.membership_id,
            self.membership_new,
        )
        self.assertEqual(
            membership_line.member_price,
            self.membership_new.list_price,
        )
        self.assertEqual(
            membership_line.date_from,
            self.membership_new.membership_date_from,
        )
        self.assertEqual(
            membership_line.date_to,
            self.membership_new.membership_date_to,
        )
