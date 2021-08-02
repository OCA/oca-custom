# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import HttpCase

from odoo.addons.http_routing.models.ir_http import slug


class TestPSCTeamsController(HttpCase):
    def setUp(self):
        super(TestPSCTeamsController, self).setUp()

        self.test_project = self.browse_ref("oca_psc_team.project_project_1_demo")

    def _test_website_page(self, page, code=200):
        response = self.url_open(page)
        self.assertEqual(response.status_code, code)

    def test_psc_teams_page(self):
        self._test_website_page("/psc-teams")

    def test_psc_project_detail_page(self):
        self._test_website_page("/psc-teams/{}".format(slug(self.test_project)))

        # It should not give an error if user changes manually
        # project id in url.
        self._test_website_page("/psc-teams/{}-{}".format(self.test_project.name, 999))

        self.start_tour(
            "/psc-teams", "psc_team_project_tour", login="project_manager_demo"
        )

        project_manager_user = self.env.ref(
            "website_oca_psc_team.project_manager_user_demo"
        )
        env = self.env(user=project_manager_user)

        self.app_store_project = env.ref("oca_psc_team.project_project_1_demo")

        self.assertEqual(
            self.app_store_project.description,
            "<p>Updated Apps store project description.</p>",
        )
