# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, new_test_user, users


class TestOcaSponsor(TransactionCase):
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
        cls.industry_a, cls.industry_b = cls.env["res.partner.industry"].create([
            {"name": "ERP"}, {"name": "CRM"}
        ])

        # Users & partners
        cls.group_manager = "membership_extension.group_membership_manager"
        cls.manager = new_test_user(cls.env, "manager", groups="base.group_user," + cls.group_manager)
        cls.manager2 = new_test_user(cls.env, "manager2", groups="base.group_user," + cls.group_manager)
        cls.portal_user = new_test_user(cls.env, "sponsor", groups="base.group_portal")
        cls.sponsor = cls.portal_user.partner_id
        cls.sponsor.write({
            "grade_id": cls.grade.id,
            "is_company": True,
        })


    def test_is_sponsor(self):
        self.assertTrue(self.sponsor.is_sponsor)
        self.assertIn(
            self.sponsor,
            self.env["res.partner"].search([("is_sponsor", "=", True)])
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
        self.assertNotIn(self.country_fr, countries) # replaced by be
        self.assertIn(self.country_ch, countries) # kept

    @users("sponsor")
    def test_industry_id_to_ids(self):
        """Ensure `industry_id` is synced in `industry_ids`"""
        self.sponsor.sponsor_industry_ids = False
        self.sponsor.industry_id = self.industry_a
        self.assertEqual(self.sponsor.sponsor_industry_ids, self.industry_a)

    def test_industry_ids_to_id(self):
        """Ensure `industry_id` is defined (if empty) from `industry_ids`"""
        self.sponsor.industry_id = False
        self.sponsor.sponsor_industry_ids = self.industry_a
        self.assertEqual(self.sponsor.industry_id, self.industry_a)

        # Add another industry: no change
        self.sponsor.sponsor_industry_ids |= self.industry_b
        self.assertEqual(self.sponsor.industry_id, self.industry_a)

    @users("sponsor")
    def test_sponsor_review_irrelevant_fields(self):
        """Not 'to review' on irrelevant fields"""
        self.assertFalse(self.sponsor.sponsor_to_review)
        self.sponsor.comment = "Not a website field"
        self.assertFalse(self.sponsor.sponsor_to_review)

    @users("manager")
    def test_sponsor_review_membership_manager(self):
        """Membership Managers do not trigger `sponsor_to_review`"""
        self.assertFalse(self.sponsor.sponsor_to_review)
        self.sponsor.website_long_description = "Changed by internal"
        self.assertFalse(self.sponsor.sponsor_to_review)
    
    def test_sponsor_review_relevant(self):
        """Mark to review when relevant (portal + fields) & create activities"""
        # Marked as to review
        self.sponsor.with_user(self.portal_user).sudo().website_long_description = "<bad things>"
        self.assertTrue(self.sponsor.sponsor_to_review)

        # Activity
        def _get_activities():
            activity_type = self.env.ref("oca_sponsor.mail_activity_review_sponsor_oca")
            activities = self.sponsor.activity_ids
            return activities.filtered(lambda x: x.activity_type_id == activity_type)

        admins = self.env.ref(self.group_manager).users
        self.assertEqual(_get_activities().mapped("user_id"), admins)

        # No duplicate activity on 2nd+ updates
        self.website_short_description = "Quick update"
        self.assertEqual(_get_activities().mapped("user_id"), admins)

        self.sponsor.with_user(self.manager).button_sponsor_review_accept()
        self.assertEqual(self.sponsor.sponsor_to_review, False)
        self.assertEqual(len(_get_activities()), 0)

    def test_search_fetch_partner_order_with_context(self):
        """Sponsors to be reviewed are displayed first"""
        ResPartner = self.env["res.partner"]
        sponsor2 = ResPartner.create({
            "name": "Sponsor Corp 2",
            "grade_id": self.grade.id,
            "is_company": True,
        })

        def _get_first_sponsor():
            return ResPartner.with_context(membership_sponsor=True).search_fetch(
                [("id", "in", (self.sponsor | sponsor2).ids)],
                ["name", "sponsor_to_review"],
            )[0]
        self.assertEqual(_get_first_sponsor(), self.sponsor)
        sponsor2.sponsor_to_review = True
        self.assertEqual(_get_first_sponsor(), sponsor2)
