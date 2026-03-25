# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.oca_sponsor.tests.test_oca_sponsor import (
    TestOcaSponsor
)
from ..schemas import Company


class TestOcaCompaniesSearchEngine(TestOcaSponsor):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_companies_json_output(self):
        sponsor = self.env["res.partner"].create({
            "name": "Full Sponsor",
            "is_company": True,
            "grade_id": self.grade.id,
            "is_published": True,
            "sponsor_to_review": False,
            "website": "https://fullsponsor.com",
            "email": "contact@fullsponsor.com",
            "website_long_description": "We are a great sponsor.",
            "website_description_why_sponsoring": "Because OCA rocks.",
            "sponsor_industry_ids": [(6, 0, [self.industry_a.id, self.industry_b.id])],
        })
        data = Company.from_record(sponsor).model_dump(mode="json")["sponsorship"]

        # Test a few data
        self.assertEqual(data["level"]["name"], self.grade.name)
        industry_names = [i["name"] for i in data["industries"]]
        self.assertIn("ERP", industry_names)


    def _in_index(self, partner, with_sync_active=False):
        in_index = partner._get_bindings().filtered(
            lambda x: x.state not in ["to_delete", "deleting"]
        )
        if with_sync_active:
            return in_index and partner._filter_add_to_oca_search_engine()
        else:
            return in_index
    
    def test_standard_partner(self):
        """A standard partner is not published (can_be_published)"""
        partner = self.env["res.partner"].create({
            "name": "Standard Corp",
            "is_company": True,
            "is_published": True,
        })
        self.assertFalse(self._in_index(partner))

    def test_becomes_integrator_autopublished(self):
        """A sponsor or a partner becoming sponsor is auto-published"""
        # create
        partner = self.env["res.partner"].create({
            "name": "Synced-as-light Sponsor",
            "is_company": True,
            "grade_id": self.grade.id,
        })
        self.assertTrue(partner.can_be_published)
        self.assertTrue(partner.is_published)
        self.assertTrue(self._in_index(partner, with_sync_active=True))

        # write
        partner2 = self.env["res.partner"].create({
            "name": "Future Sponsor",
            "is_company": True,
        })
        partner2.grade_id = self.grade
        self.assertTrue(self._in_index(partner2, with_sync_active=True))

        # test _search_can_be_published
        results = self.env["res.partner"].search([("can_be_published", "=", True)])
        self.assertIn(partner2, results)

    def test_partner_unpublished(self):
        """Any published partner can be unpublished with `is_published`"""
        partner = self.env["res.partner"].create({
            "name": "Partner not to publish",
            "is_company": True,
            "grade_id": self.grade.id,
        })
        self.assertTrue(self._in_index(partner, with_sync_active=True))
        partner.is_published = False # manually prevent publishing
        self.assertFalse(self._in_index(partner))

    def test_sponsor_to_review_not_in_index(self):
        """Sponsor with pending review *is* in index, but its synced is paused"""
        self.assertTrue(self._in_index(self.sponsor, with_sync_active=True))
        self.sponsor.with_user(self.portal_user).sudo().website_long_description = "Updated from portal"
        self.assertTrue(self.sponsor.sponsor_to_review)
        self.assertTrue(self._in_index(self.sponsor, with_sync_active=False))
        self.assertFalse(self._in_index(self.sponsor, with_sync_active=True))
