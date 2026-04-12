# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tools import mute_logger

from odoo.addons.oca_sponsor.tests.test_oca_sponsor import TestOcaSponsorCommon

from ..schemas.res_partner_company import Company


class TestOcaCompaniesSearchEngine(TestOcaSponsorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        se_group_manager = cls.env.ref(
            "connector_search_engine.group_connector_search_engine_manager"
        )
        cls.manager.groups_id = [Command.link(se_group_manager.id)]

    def test_companies_json_output(self):
        sponsor = self.env["res.partner"].create(
            {
                "name": "Full Sponsor",
                "is_company": True,
                "grade_id": self.grade.id,
                "is_published": True,
                "sponsor_to_review": False,
                "website": "https://fullsponsor.com",
                "email": "contact@fullsponsor.com",
                "website_long_description": "We are a great sponsor.",
                "website_description_why_sponsoring": "Because OCA rocks.",
                "sponsor_industry_ids": [
                    (6, 0, [self.industry_a.id, self.industry_b.id])
                ],
            }
        )
        data = Company.from_record(sponsor).model_dump(mode="json")["sponsorship"]

        # Test a few data
        self.assertEqual(data["level"]["name"], self.grade.name)
        industry_names = [i["name"] for i in data["industries"]]
        self.assertIn("ERP", industry_names)

    def _in_index(self, partner, with_sync_active=False):
        not_states = ["to_delete", "deleting"]
        if with_sync_active:
            not_states += ["recompute_error", "invalid_data"]

        bindings = partner._get_bindings()
        return not bool(bindings.filtered(lambda x: x.state in not_states))

    def test_becomes_integrator_autopublished(self):
        """A sponsor or a partner becoming sponsor is auto-published"""
        # create
        partner = self.env["res.partner"].create(
            {
                "name": "Synced-as-light Sponsor",
                "is_company": True,
                "grade_id": self.grade.id,
            }
        )
        self.assertTrue(partner.is_published)
        self.assertTrue(self._in_index(partner, with_sync_active=True))

        # write
        partner2 = self.env["res.partner"].create(
            {
                "name": "Future Sponsor",
                "is_company": True,
            }
        )
        partner2.grade_id = self.grade
        self.assertTrue(self._in_index(partner2, with_sync_active=True))

    def test_partner_unpublished(self):
        """Any published partner can be unpublished with `is_published`"""
        partner = self.env["res.partner"].create(
            {
                "name": "Partner not to publish",
                "is_company": True,
                "grade_id": self.grade.id,
            }
        )
        self.assertTrue(self._in_index(partner, with_sync_active=True))
        partner.is_published = False  # manually prevent publishing
        self.assertFalse(self._in_index(partner))

    @mute_logger("odoo.addons.connector_search_engine.models.se_binding")
    def test_sponsor_to_review_not_in_index(self):
        """Sponsor with pending review *is* in index, but its synchro is paused"""
        self.assertTrue(self._in_index(self.sponsor, with_sync_active=True))
        self.sponsor.with_user(
            self.portal_user
        ).sudo().website_long_description = "Updated from portal"
        self.assertTrue(self.sponsor.sponsor_to_review)

        self.sponsor._get_bindings().recompute_json()  # logs an Exception
        # transitory state
        self.assertTrue(self._in_index(self.sponsor, with_sync_active=False))
        self.assertFalse(self._in_index(self.sponsor, with_sync_active=True))
