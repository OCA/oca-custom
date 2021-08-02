# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import odoo.tests
from odoo.tools import config


@odoo.tests.tagged("post_install", "-at_install")
class TestUi(odoo.tests.HttpCase):
    def setUp(self):
        super().setUp()
        # Trick this configuration value for avoiding an error
        config["source_code_local_path"] = "/tmp/"
        partner = self.env["res.partner"].create(
            {
                "name": "Integrator test",
                "email": "integrator.test@example.com",
                "is_company": True,
                "street": "Palermo, Capital Federal",
                "city": "Vivegnis",
                "country_id": self.browse_ref("base.in").id,
                "website_published": True,
                "child_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Diane Sanford",
                            "website_published": True,
                            "github_name": "demo-git-diane",
                        },
                    )
                ],
            }
        )
        self.env["res.users"].create(
            {
                "partner_id": partner.id,
                "login": "integrator",
                "password": "integrator",
                "groups_id": [(6, 0, self.browse_ref("base.group_portal").ids)],
            }
        )
        self.env["odoo.author"].create(
            {
                "name": "Odoo Author Test",
                "partner_id": partner.id,
            }
        )
        product_template = self.env["product.template"].create(
            {
                "name": "Prod. Tmpl. test",
                "is_published": True,
            }
        )
        odoo_module = self.env["odoo.module"].create(
            {
                "technical_name": "odoo_module_test",
                "product_template_id": product_template.id,
            }
        )
        product_template.odoo_module_id = odoo_module.id
        organization = self.env["github.organization"].create(
            {
                "name": "Organization Organization Test",
                "github_name": "organization_test_login",
            }
        )
        repository = self.env["github.repository"].create(
            {
                "name": "repository_test",
                "organization_id": organization.id,
            }
        )
        branch = self.env["github.repository.branch"].create(
            {
                "name": "branch test",
                "repository_id": repository.id,
                "organization_id": organization.id,
            }
        )
        self.env["odoo.module.version"].create(
            {
                "name": "Odoo Module test",
                "technical_name": "odoo_module_test",
                "module_id": odoo_module.id,
                "repository_branch_id": branch.id,
                "author": "Odoo Author Test",
            }
        )
        partner._compute_developed_modules()

    def test_integrator_portal(self):
        self.start_tour("/my/account", "integrator_portal", login="integrator")

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
