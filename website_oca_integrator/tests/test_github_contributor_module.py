# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import responses

from odoo.tests.common import SavepointCase


class TestGithubContributorModule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].set_param("github.access_token", "test")
        cls.partner = cls.env["res.partner"]
        cls.partner.search([]).is_published = False
        cls.company3 = cls.partner.create(
            {
                "name": "Partner 3",
                "is_company": True,
                "is_published": True,
                "github_organization": "company3_github_name",
            }
        )
        cls.contributor1 = cls.partner.create(
            {
                "name": "Contributor 1",
                "is_company": False,
                "github_name": "contributor1_github_name",
                "is_published": True,
                "parent_id": cls.company3.id,
            }
        )
        for i in range(1, 7):
            template = cls.env["product.template"].create(
                {
                    "name": f"Prod. Tmpl. demo {i}",
                    "is_published": True,
                }
            )
            odoo_module = cls.env["odoo.module"].create(
                {
                    "technical_name": f"odoo_module{i}",
                    "product_template_id": template.id,
                }
            )
            template.odoo_module_id = odoo_module.id
        cls.last_product_template = template
        cls.github_api_response()

    @classmethod
    def github_api_response(cls):
        """
        Static event responses from github api to mock github calls.
        """
        cls.add_response(
            "https://api.github.com:443/users/contributor1_github_name",
            {
                "login": "contributor1_github_name",
                "url": "https://api.github.com/users/contributor1_github_name",
                "events_url": "https://api.github.com/users/"
                "contributor1_github_name/events{/privacy}",
            },
        )
        cls.add_response(
            "https://api.github.com:443/users/contributor1_github_name/events",
            [
                {
                    "type": "PullRequestEvent",
                    "actor": {"login": "contributor3_github_name"},
                    "repo": {
                        "name": "OCA/oca-test-custom",
                        "url": "https://api.github.com/repos/OCA/oca-test-custom",
                    },
                    "payload": {
                        "action": "opened",
                        "pull_request": {"number": 2290},
                    },
                    "org": {"login": "OCA"},
                }
            ],
        )
        cls.add_response(
            "https://api.github.com:443/repos/OCA/oca-test-custom/pulls/2290",
            {
                "id": 200401025,
                "merged_at": "2018-07-10T12:01:59Z",
                "merged": True,
                "head": {"sha": "385ad61205a8b7e00c97d06cf0e192924e2cc4f7"},
            },
        )
        cls.add_response(
            "https://api.github.com:443/repos/OCA/oca-test-custom/commits/"
            "385ad61205a8b7e00c97d06cf0e192924e2cc4f7",
            {
                "sha": "385ad61205a8b7e236347d06cf0e192924e2cc4f7",
                "files": [
                    {"filename": "odoo_module1/readme.rst"},
                    {"filename": "odoo_module2/readme.rst"},
                    {"filename": "odoo_module3/readme.rst"},
                    {"filename": "odoo_module4/readme.rst"},
                    {"filename": "odoo_module5/readme.rst"},
                    {"filename": "odoo_module6/readme.rst"},
                ],
            },
        )

    @classmethod
    def add_response(cls, url, json):
        responses.add(responses.GET, url, json=json, status=200)

    def test_website_published_contributors(self):
        contributors = self.partner.search(
            ["&", ("github_name", "!=", False), ("website_published", "=", True)]
        )
        contributor_ids = self.partner.get_contributors().ids
        self.assertEqual(contributors.ids, contributor_ids)

    @responses.activate
    def test_contributor_five_modules(self):
        self.contributor1.write(
            {
                "contributor_module_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_template_id": self.last_product_template.id,
                            "date_pr_merged": "2018-08-12",
                            "partner_id": self.contributor1.id,
                        },
                    )
                ]
            }
        )
        self.partner.cron_create_github_user_module()
        module_lines = self.env["contributor.module.line"].search(
            [("partner_id", "=", self.contributor1.id)]
        )
        self.assertEqual(len(module_lines), 5)
        self.assertListEqual(
            module_lines.mapped("product_template_id.technical_name"),
            [f"odoo_module{i}".format(i) for i in range(1, 6)],
        )

    def test_error_fetching_user(self):
        logger = "odoo.addons.website_oca_integrator.models.res_partner"
        level = "WARNING"
        with self.assertLogs(logger, level) as log_catcher:
            self.partner.cron_create_github_user_module()
        self.assertEqual(
            log_catcher.output[0],
            "{}:{}:Error while fetching user 'Contributor 1'.".format(level, logger),
        )
