# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, new_test_user, users


class TestOcaSponsorCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Sponsor grade
        cls.grade = cls.env["res.partner.grade"].create({"name": "Gold"})
        # Countries
        cls.country_fr = cls.env.ref("base.fr")
        cls.country_be = cls.env.ref("base.be")
        cls.country_ch = cls.env.ref("base.ch")
        # Industries
        cls.industry_a, cls.industry_b = cls.env["res.partner.industry"].create(
            [{"name": "ERP"}, {"name": "CRM"}]
        )

        # Users & partners
        cls.manager = new_test_user(
            cls.env, "manager", groups="base.group_user,base.group_partner_manager"
        )
        cls.env.ref(
            "oca_sponsor.mail_activity_team_sponsor_reviewers"
        ).member_ids |= cls.manager
        cls.portal_user = new_test_user(cls.env, "sponsor", groups="base.group_portal")
        cls.sponsor = cls.portal_user.partner_id
        cls.sponsor.with_user(cls.manager).write(
            {
                "grade_id": cls.grade.id,
                "is_company": True,
                "country_id": cls.country_fr.id,
                "website_long_description": "Initial description",
            }
        )


class TestOcaSponsor(TestOcaSponsorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_is_sponsor_search(self):
        self.assertTrue(self.sponsor.is_sponsor)
        self.assertIn(
            self.sponsor, self.env["res.partner"].search([("is_sponsor", "=", True)])
        )

    @users("sponsor")
    def test_sponsor_country_ids(self):
        """Ensure `country_id` is always in `sponsor_country_ids`
        and that countries manually input stay in `sponsor_country_ids`
        """
        self.sponsor.sponsor_country_ids = self.country_ch
        self.sponsor.country_id = self.country_fr
        self.sponsor.country_id = self.country_be

        countries = self.sponsor.sponsor_country_ids
        self.assertIn(self.country_be, countries)
        self.assertNotIn(self.country_fr, countries)  # replaced by be
        self.assertIn(self.country_ch, countries)  # kept

    @users("sponsor")
    def test_industry_id_to_ids(self):
        """Ensure `industry_id` is synced in `industry_ids` (same than country)"""
        self.sponsor.sponsor_industry_ids = False
        self.sponsor.industry_id = self.industry_a
        self.assertEqual(self.sponsor.sponsor_industry_ids, self.industry_a)

    @users("sponsor")
    def test_sponsor_review_irrelevant_fields(self):
        """No 'review' mode when changing non-sponsor fields"""
        sponsor = self.sponsor.with_user(self.portal_user).sudo()
        self.assertFalse(sponsor.sponsor_to_review)

        sponsor.comment = "Not a website field"
        self.assertFalse(sponsor.sponsor_to_review)

        # Relevant field but no value change => should not trigger review process
        sponsor.website_long_description = "Initial description"
        self.assertFalse(sponsor.sponsor_to_review)

    @users("manager")
    def test_sponsor_review_membership_manager(self):
        """Membership Managers do not trigger `sponsor_to_review`"""
        self.assertFalse(self.sponsor.sponsor_to_review)
        self.sponsor.with_user(
            self.manager
        ).website_long_description = "Changed by internal"
        self.assertFalse(self.sponsor.sponsor_to_review)

    @users("sponsor")
    def test_sponsor_review_relevant(self):
        """Mark to review when relevant (portal + fields) & create activities"""
        self.sponsor.with_user(
            self.portal_user
        ).sudo().website_long_description = "text to review"
        self.assertTrue(self.sponsor.sponsor_to_review)
        self.assertIn(self.manager, self.sponsor.activity_team_user_ids)

    @users("manager")
    def test_sponsor_review_validate(self):
        """Test approval"""
        self.sponsor._set_sponsor_to_review()
        self.sponsor.with_user(self.manager).button_sponsor_review_accept()
        self.assertFalse(self.sponsor.sponsor_to_review)
        self.assertNotIn(self.manager, self.sponsor.activity_team_user_ids)

    def test_search_fetch_partner_order_with_context(self):
        """Sponsors to be reviewed are displayed first"""
        ResPartner = self.env["res.partner"]
        sponsor2 = ResPartner.with_user(self.manager).create(
            [
                {
                    "name": "Sponsor Corp 2",
                    "grade_id": self.grade.id,
                    "is_company": True,
                    "sponsor_to_review": False,
                }
            ]
        )
        self.sponsor.sponsor_to_review = True
        sponsors = self.sponsor | sponsor2

        def _get_first_sponsor():
            return ResPartner.with_context(membership_sponsor=True).search_fetch(
                [("id", "in", sponsors.ids)],
                ["name", "sponsor_to_review"],
            )[0]

        self.assertEqual(_get_first_sponsor(), self.sponsor)
        self.sponsor.sponsor_to_review = False
        sponsor2.sponsor_to_review = True
        self.assertEqual(_get_first_sponsor(), sponsor2)
