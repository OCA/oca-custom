# Copyright 2026 Akretion (https://www.akretion.com).
# @author Benoit GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import Command, fields
from odoo.tests import TransactionCase


class TestOcaMembershipSubscription(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test.partner@example.com",
            }
        )
        cls.delegated_member = cls.env["res.partner"].create(
            {
                "name": "Delegated Member",
                "email": "delegated.member@example.com",
                "parent_id": cls.partner.id,
            }
        )

        cls.membership_product = cls.env["product.product"].create(
            {
                "name": "Membership Product",
                "list_price": 100.0,
                "subscribable": True,
                "taxes_id": [Command.set(cls.tax_0pc.ids)],
                "membership": True,
            }
        )

        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "Test Membership Template",
                "code": "test_membership_template",
                "description": "Membership subscription template",
                "product_ids": [Command.set([cls.membership_product.id])],
                "recurring_rule_type": "years",
                "recurring_interval": 1,
                "recurring_rule_boundary": "unlimited",
            }
        )

        cls.subscription = cls.env["sale.subscription"].create(
            {
                "company_id": cls.env.ref("base.main_company").id,
                "partner_id": cls.partner.id,
                "template_id": cls.template.id,
                "date_start": fields.Date.today(),
                "recurring_next_date": fields.Date.today(),
            }
        )
        cls.subscription_line = cls.env["sale.subscription.line"].create(
            {
                "company_id": cls.env.ref("base.main_company").id,
                "sale_subscription_id": cls.subscription.id,
                "product_id": cls.membership_product.id,
                "partner_id": cls.delegated_member.id,
            }
        )

    def test_prepare_account_move_line_with_delegated_member(self):
        """Test _prepare_account_move_line with delegated member"""
        vals = self.subscription_line._prepare_account_move_line()

        self.assertIn("start_date", vals)
        self.assertEqual(vals["start_date"], self.subscription.recurring_next_date)

        # Check that end_date is calculated correctly
        self.assertIn("end_date", vals)
        expected_end_date = self.subscription.recurring_next_date + relativedelta(
            **{
                self.subscription.template_id.recurring_rule_type: int(
                    self.subscription.template_id.recurring_interval
                )
            }
        )
        self.assertEqual(vals["end_date"], expected_end_date)

        # Check that delegated_member_id is set
        self.assertIn("delegated_member_id", vals)
        self.assertEqual(vals["delegated_member_id"], self.delegated_member.id)
