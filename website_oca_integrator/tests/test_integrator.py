# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import datetime

from dateutil.relativedelta import relativedelta

from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestIntegratorAssign(AccountingTestCase):
    def setUp(self):
        super(TestIntegratorAssign, self).setUp()

        self.partner = self.env["res.partner"]

        # company section
        self.company1 = self.partner.create(
            {
                "name": "Partner 1",
                "is_company": True,
                "website_published": True,
                "github_organization": "company1_github_login",
            }
        )

        self.company2 = self.partner.create(
            {"name": "Partner 2", "is_company": True, "website_published": False}
        )

        # customer section
        self.customer1 = self.partner.create(
            {
                "name": "Customer 1",
                "is_company": False,
                "github_login": "customer1_github_login",
                "website_published": True,
                "parent_id": self.company1.id,
            }
        )

        self.customer2 = self.partner.create(
            {
                "name": "Customer 2",
                "is_company": False,
                "website_published": True,
                "parent_id": self.company2.id,
            }
        )

        # membership section
        self.membership_product = self.env["product.product"].create(
            {
                "name": "Basic Membership",
                "membership": True,
                "membership_date_from": datetime.date.today() + relativedelta(days=-2),
                "membership_date_to": datetime.date.today() + relativedelta(months=1),
                "type": "service",
                "list_price": 100.00,
            }
        )

        self.bank_journal = self.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )

    def create_member_invoice(self, customer):
        customer.create_membership_invoice(
            product_id=self.membership_product.id, datas={"amount": 75.0}
        )
        invoice = self.env["account.invoice"].search(
            [("partner_id", "=", customer.id)], limit=1
        )
        invoice.action_invoice_open()
        invoice.pay_and_reconcile(self.bank_journal, invoice.amount_total)

    def test_integrators(self):
        # contact has github login and not a paid member
        self.company1._compute_integrator()
        self.assertEqual(
            self.company1.is_integrator,
            True,
            "Partner's contact who has github login, \
                         should be counted as integrator.",
        )

        # contact has no github login and not a paid member
        self.company2._compute_integrator()
        self.assertEqual(
            self.company2.is_integrator,
            False,
            "Partner's contact who has no github login or not \
                        a paid member should not be counted as integrator.",
        )

        # contact has no github login and a paid member
        self.create_member_invoice(self.customer2)
        self.assertEqual(
            self.company2.is_integrator,
            True,
            "Partner's contact who is paid member \
                         should be counted as integrator.",
        )

    def test_contributors_count(self):
        # partner contact has github login
        self.company1._compute_contributor_count()
        self.assertEqual(
            self.company1.contributor_count,
            1,
            "If partner's contact has github login then \
                          partner should be considered as contributor.",
        )

        # check contributor count if partner contact does not have github login
        self.company2._compute_contributor_count()
        self.assertEqual(
            self.company2.contributor_count,
            0,
            "If partner's all contact does not have github login \
                         then contributor count should be displayed as 0.",
        )

    def test_members_count(self):
        # check member count if partner contact does not have paid member
        self.company2._compute_member_count()
        self.assertEqual(
            self.company2.member_count,
            0,
            "If partner's all contact does not have paid  \
                         membership then member count should be \
                         displayed as 0.",
        )

        # check member count if partner contact has paid member
        self.create_member_invoice(self.customer2)
        self.company2._compute_member_count()
        self.assertEqual(
            self.company2.member_count,
            1,
            "If partner's contact has paid member \
                         then, partner should be considered as member.",
        )

    def test_not_integrator(self):
        self.company1.write({"is_company": False})
        self.assertEqual(self.company1.github_organization, False)
