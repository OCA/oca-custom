# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import config


@tagged("post_install", "-at_install")
class TestIntegratorAssign(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Trick this configuration value for avoiding an error
        config["source_code_local_path"] = "/tmp/"

        cls.Partner = cls.env["res.partner"].sudo()
        cls.country_india = cls.env.ref("base.in")

        # ---------------------------------------------------------------------
        # Company section
        # ---------------------------------------------------------------------
        cls.company1 = cls.Partner.create(
            {
                "name": "Partner 1",
                "is_company": True,
                "website_published": True,
                "github_organization": "company1_github_name",
                "country_id": cls.country_india.id,
            }
        )

        cls.company2 = cls.Partner.create(
            {
                "name": "Partner 2",
                "is_company": True,
                "website_published": False,
                "country_id": cls.country_india.id,
            }
        )

        # ---------------------------------------------------------------------
        # Customer/Contact section
        # ---------------------------------------------------------------------
        cls.customer1 = cls.Partner.create(
            {
                "name": "Customer 1",
                "is_company": False,
                "github_name": "customer1_github_name",
                "website_published": True,
                "parent_id": cls.company1.id,
                "country_id": cls.country_india.id,
            }
        )

        cls.customer2 = cls.Partner.create(
            {
                "name": "Customer 2",
                "is_company": False,
                "website_published": True,
                "parent_id": cls.company2.id,
                "country_id": cls.country_india.id,
            }
        )

    def test_contributors_count(self):
        self.company1._compute_contributor_count()
        self.assertEqual(
            self.company1.contributor_count,
            1,
            "If a partner has a contact with github login, "
            "contributor_count should be 1.",
        )

        self.company2._compute_contributor_count()
        self.assertEqual(
            self.company2.contributor_count,
            0,
            "If a partner has no contacts with github login, "
            "contributor_count should be 0.",
        )

    def test_members_count(self):
        self.company2._compute_member_count()
        self.assertEqual(
            self.company2.member_count,
            0,
            "If partner has no paid membership contacts, " "member_count should be 0.",
        )

        self.customer2.write({"membership_state": "paid"})
        self.company2.invalidate_recordset()
        self.company2._compute_member_count()

        self.assertEqual(
            self.company2.member_count,
            1,
            "If partner has a paid member contact, member_count should be 1.",
        )

    def test_not_integrator(self):
        self.company1.write({"is_company": False})
        self.assertEqual(self.company1.github_organization, False)
