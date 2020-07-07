# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import mock

from odoo.tests.common import TransactionCase

from odoo.addons.github_connector.models.github import Github

partner = "odoo.addons.website_oca_integrator.models.res_partner.ResPartner"
github_model = (
    "odoo.addons.github_connector.models" ".abstract_github_model.AbstractGithubModel"
)


class TestGithubContributorModule(TransactionCase):
    def setUp(self):
        super(TestGithubContributorModule, self).setUp()

        self.partner = self.env["res.partner"]

        self.company3 = self.partner.create(
            {
                "name": "Partner 3",
                "is_company": True,
                "website_published": True,
                "github_organization": "company3_github_login",
            }
        )

        self.contributor1 = self.partner.create(
            {
                "name": "Contributor 1",
                "is_company": False,
                "github_login": "contributor1_github_login",
                "website_published": True,
                "parent_id": self.company3.id,
            }
        )

    def github_api_response(self):
        """
        Static event responses from github api to mock github calls.
        """
        event_response = [
            {
                "id": "3421739241",
                "type": "PullRequestEvent",
                "actor": {"login": "contributor3_github_login"},
                "payload": {
                    "action": "opened",
                    "pull_request": {
                        "url": "https://api.github.com/repos"
                        "/OCA/oca-test-custom/pulls/2290",
                        "commits_url": "https://api.github.com/repos"
                        "/OCA/oca-test-custom/pulls/12/commits",
                        "head": {
                            "sha": "385ad61205a8b7e00c97d06cf0e192924e2cc4f7",
                            "repo": {
                                "commits_url": "https://api.github.com/repos"
                                "/contributor3_github_login"
                                "/oca-test-custom/commits{/sha}"
                            },
                        },
                    },
                },
                "org": {"login": "OCA"},
            }
        ]
        pr_response = {
            "id": 200401025,
            "merged_at": "2018-07-10T12:01:59Z",
            "merged": True,
        }
        commit_response = {
            "sha": "385ad61205a8b7e55c97d06cf0e192924e2cc4f7",
            "files": [
                {"filename": "odoo_module1/readme.rst"},
                {"filename": "odoo_module2/readme.rst"},
                {"filename": "odoo_module3/readme.rst"},
                {"filename": "odoo_module4/readme.rst"},
                {"filename": "odoo_module5/readme.rst"},
                {"filename": "odoo_module6/readme.rst"},
            ],
        }
        commit_response2 = {
            "sha": "385ad61205a8b7e236347d06cf0e192924e2cc4f7",
            "files": [{"filename": "odoo_module1/readme.rst"}],
        }
        return event_response, pr_response, commit_response, commit_response2

    def get_github_connector(self):
        return Github(
            "user",
            False,
            False,
            int(self.env["ir.config_parameter"].get_param("github.max_try")),
        )

    def test_website_published_contributors(self):
        contributors = self.partner.search(
            ["&", ("github_login", "!=", False), ("website_published", "=", True)]
        )
        contributor_ids = self.partner.get_contributors().ids
        self.assertEqual(contributors.ids, contributor_ids)

    def test_contributor_modules(self):
        with mock.patch("%s.get_contributors" % partner) as contributor:
            contributor.return_value = self.contributor1
            with mock.patch("%s.get_github_api_response" % partner) as api_response:
                (
                    event_response,
                    pr_response,
                    commit_response,
                    commit_response2,
                ) = self.github_api_response()
                api_response.side_effect = [
                    event_response,
                    pr_response,
                    commit_response2,
                    [],
                ]
                with mock.patch(
                    "%s.get_github_connector" % github_model
                ) as github_api_connector:
                    github_api_connector.return_value = self.get_github_connector()
                    self.partner.cron_create_github_user_module()

            module_lines = self.env["contributor.module.line"].search(
                [("partner_id", "=", self.contributor1.id)]
            )

            self.assertEqual(len(module_lines), 1)

    def test_contributor_five_modules(self):
        self.product_template6_id = self.browse_ref(
            "website_oca_integrator.odoo_module_6_demo"
        ).product_template_id

        self.contributor1.write(
            {
                "contributor_module_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_template_id": self.product_template6_id.id,
                            "date_pr_merged": "12-08-2018",
                            "partner_id": self.contributor1.id,
                        },
                    )
                ]
            }
        )

        with mock.patch("%s.get_contributors" % partner) as contributor:
            contributor.return_value = self.contributor1
            with mock.patch("%s.get_github_api_response" % partner) as api_response:
                (
                    event_response,
                    pr_response,
                    commit_response,
                    commit_response2,
                ) = self.github_api_response()
                api_response.side_effect = [
                    event_response,
                    pr_response,
                    commit_response,
                ]
                with mock.patch(
                    "%s.get_github_connector" % github_model
                ) as github_api_connector:
                    github_api_connector.return_value = self.get_github_connector()
                    self.partner.cron_create_github_user_module()

            self.product_template_id = self.browse_ref(
                "website_oca_integrator.odoo_module_1_demo"
            ).product_template_id

            module_lines = self.env["contributor.module.line"].search(
                [("partner_id", "=", self.contributor1.id)]
            )

            self.assertEqual(len(module_lines), 5)

    def test_log_wrong_github_event_url(self):
        with mock.patch("%s.get_contributors" % partner) as contributor:
            contributor.return_value = self.contributor1
            with mock.patch(
                "%s.get_github_connector" % github_model
            ) as github_api_connector:
                github_api_connector.return_value = self.get_github_connector()
                with mock.patch("logging.Logger.warning") as log:
                    self.partner.cron_create_github_user_module()
                    log.assert_called_with(
                        "Github login for partner '%s' is not"
                        " correctly set." % (self.contributor1.name)
                    )

    def test_log_wrong_pull_request_url(self):
        (
            event_response,
            pr_response,
            commit_response,
            commit_response2,
        ) = self.github_api_response()
        github_api_connector = self.get_github_connector()
        github_orgs = self.partner.get_github_organization()

        with mock.patch("logging.Logger.warning") as log:
            self.partner.get_github_user_modules(
                event_response, github_api_connector, 0, github_orgs
            )
            url = event_response[0]["payload"]["pull_request"]["url"]
            log.assert_called_with(
                "Error while calling url '%s' during fetching "
                "module for '%s'." % (url, event_response[0]["actor"]["login"])
            )

    def test_log_wrong_commit_url(self):
        (
            event_response,
            pr_response,
            commit_response,
            commit_response2,
        ) = self.github_api_response()
        github_api_connector = self.get_github_connector()
        github_orgs = self.partner.get_github_organization()

        with mock.patch("%s.get_github_api_response" % partner) as api_response:
            api_response.side_effect = [pr_response]
            with mock.patch("logging.Logger.warning") as log:
                pull_request = event_response[0]["payload"]["pull_request"]

                commit_sha = pull_request["head"]["sha"]
                commit_url = pull_request["head"]["repo"]["commits_url"].replace(
                    "{/sha}", "/" + commit_sha
                )

                self.partner.get_github_user_modules(
                    event_response, github_api_connector, 0, github_orgs
                )

                log.assert_called_with(
                    "Error while calling url '%s' during fetching "
                    "module for '%s'."
                    % (commit_url, event_response[0]["actor"]["login"])
                )

    def test_get_github_user_modules(self):
        github_orgs = self.partner.get_github_organization()
        with mock.patch("%s.get_github_api_response" % partner) as api_response:
            (
                event_response,
                pr_response,
                commit_response,
                commit_response2,
            ) = self.github_api_response()
            api_response.side_effect = [pr_response, commit_response]

            github_api_connector = self.get_github_connector()
            module_lines = self.partner.get_github_user_modules(
                event_response, github_api_connector, 0, github_orgs
            )

        self.assertEqual(len(module_lines), 5)

    def test_update_contributor_modules(self):
        modules = {
            "odoo_module1": "2018-07-10T10:06:19Z",
            "odoo_module2": "2018-06-13T11:01:29Z",
            "odoo_module3": "2018-05-12T09:08:25Z",
            "odoo_module4": "2018-04-12T12:02:05Z",
        }
        self.partner.update_contributor_modules(self.contributor1, modules)
        self.assertEqual(
            len(self.contributor1.contributor_module_line_ids), len(modules)
        )
