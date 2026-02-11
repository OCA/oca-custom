# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import HttpCase
from odoo.tools import config


class TestIntegratorController(HttpCase):
    def setUp(self):
        super().setUp()

        # Trick this configuration value for avoiding an error
        config["source_code_local_path"] = "/tmp/"

        Partner = self.env["res.partner"].sudo()
        self.country_india = self.env.ref("base.in")

        self.partner = Partner.create(
            {
                "name": "Partner Test",
                "is_company": True,
                "email": "partner.test@yourcompany.example.com",
                "city": "Vivegnis",
                "street": "Palermo, Capital Federal",
                "country_id": self.country_india.id,
                "website_published": True,
            }
        )

        self.contact1 = Partner.create(
            {
                "name": "Contact 1 Test",
                "parent_id": self.partner.id,
                "github_name": "demo-git-rusty",
                "website_published": True,
                "membership_state": "paid",
                "country_id": self.country_india.id,
            }
        )

        self.contact2 = Partner.create(
            {
                "name": "Contact 2 Test",
                "parent_id": self.partner.id,
                "github_name": "demo-git-diane",
                "website_published": True,
                "membership_state": "paid",
                "country_id": self.country_india.id,
            }
        )

    def _test_website_page(self, page, code=200):
        response = self.url_open(page)
        self.assertEqual(response.status_code, code)

    def test_unknown_integrator(self):
        self._test_website_page("/integrators/test-integrator")

    def test_integrator_page(self):
        # Avoid slug() import: Odoo model routes accept plain IDs too.
        self._test_website_page(f"/integrators/country/{self.country_india.id}")
        self._test_website_page("/integrators")
        self._test_website_page(f"/integrators?search={self.partner.name}")
        self._test_website_page("/integrators?country_all=True")

    def test_integrator_detail_page(self):
        self._test_website_page(f"/integrators/country/{self.country_india.id}")
        self._test_website_page(f"/integrators/{self.partner.id}")
        self._test_website_page(
            f"/integrators/{self.partner.id}?country_id={self.country_india.id}"
        )

    def test_contributor_list_page(self):
        self._test_website_page(
            f"/integrators/{self.partner.id}/contributors/country/"
            f"{self.country_india.id}?search={self.partner.name}"
        )

    def test_member_page(self):
        self._test_website_page(f"/members/{self.contact1.id}")
        self._test_website_page(f"/members/{self.contact2.id}")
