# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import HttpCase
from odoo.tools import config

from odoo.addons.http_routing.models.ir_http import slug


class TestIntegratorController(HttpCase):
    def setUp(self):
        super().setUp()

        # Trick this configuration value for avoiding an error
        config["source_code_local_path"] = "/tmp/"
        self.country_india = self.browse_ref("base.in")
        self.partner = self.env["res.partner"].create(
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
        self.contact1 = self.env["res.partner"].create(
            {
                "name": "Contact 2 Test",
                "parent_id": self.partner.id,
                "github_name": "demo-git-rusty",
            }
        )
        self.contact2 = self.env["res.partner"].create(
            {
                "name": "Contact 2 Test",
                "parent_id": self.partner.id,
                "github_name": "demo-git-diane",
            }
        )

    def _test_website_page(self, page, code=200):
        response = self.url_open(page)
        self.assertEqual(response.status_code, code)

    def test_unknown_integrator(self):
        self._test_website_page("/integrators/test-integrator")

    def test_integrator_page(self):
        self._test_website_page("/integrators/country/{}".format(self.country_india.id))
        self._test_website_page("/integrators")
        self._test_website_page("/integrators?search=%s" % self.partner.name)
        self._test_website_page("/integrators?&country_all=True")

    def test_integrator_detail_page(self):
        self._test_website_page("/integrators/country/{}".format(self.country_india.id))

        self._test_website_page("/integrators/{}".format(slug(self.partner)))

        self._test_website_page(
            "/integrators/{}?country_id={}".format(
                slug(self.partner), self.country_india.id
            )
        )

    def test_contributor_list_page(self):
        self._test_website_page(
            "/integrators/{}/contributors/country/{}?search={}".format(
                slug(self.partner), slug(self.country_india), self.partner.name
            )
        )

    def test_member_page(self):
        self._test_website_page("/members/{}".format(slug(self.contact1)))
        self._test_website_page("/members/{}".format(slug(self.contact2)))
