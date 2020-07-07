# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import HttpCase

from odoo.addons.http_routing.models.ir_http import slug


class TestIntegratorController(HttpCase):
    def setUp(self):
        super(TestIntegratorController, self).setUp()

        self.country_india = self.browse_ref("base.in")
        self.partner = self.browse_ref(
            "website_oca_integrator.partner_integrator_portal_demo"
        )
        self.contact1 = self.browse_ref(
            "website_oca_integrator.res_partner_contact_1_demo"
        )
        self.contact2 = self.browse_ref(
            "website_oca_integrator.res_partner_contact_2_demo"
        )
        self.product_attribute = self.browse_ref(
            "website_oca_integrator.product_attribute_value_1_demo"
        )
        self.product = self.browse_ref("website_oca_integrator.product_product_1_demo")

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

    def test_product_list_page(self):
        self._test_website_page(
            "/shop?search={}&attrib={}-{}&integrator={}".format(
                self.partner.author_ids[0].module_ids[0].name,
                self.product_attribute.attribute_id.id,
                self.product_attribute.id,
                slug(self.partner),
            )
        )
        self._test_website_page(
            "/shop/category/{}-{}?integrator={}".format(
                self.product.public_categ_ids[0].name,
                self.product.public_categ_ids[0].id,
                slug(self.partner),
            )
        )
        self._test_website_page("/shop?&integrator={}".format("test-integrator"))
        self._test_website_page("/shop")
        self._test_website_page(
            "/shop?&integrator={}&ppg={}".format(slug(self.partner), "testppg")
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
