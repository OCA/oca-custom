# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def test_integrator_portal(self):
        self.browser_js(
            "/my/account",
            "odoo.__DEBUG__.services['web_tour.tour']" ".run('integrator_portal')",
            "odoo.__DEBUG__.services['web_tour.tour']" ".tours.integrator_portal.ready",
            login="integrator",
        )

        env = self.env
        partner = (
            env["res.partner"]
            .sudo()
            .search([("github_organization", "=", "test_github_organization")])
        )

        self.assertEqual(len(partner), 1)
        self.assertTrue(
            set(partner.favourite_module_ids.ids).issubset(
                set(partner.developed_module_ids.ids)
            ),
            True,
        )
