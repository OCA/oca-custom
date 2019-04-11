# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.api import Environment
from odoo.tests.common import HttpCase

from odoo.addons.http_routing.models.ir_http import slug


class TestPSCTeamsController(HttpCase):

    def setUp(self):
        super(TestPSCTeamsController, self).setUp()

        self.test_project = self.browse_ref(
            'oca_psc_team.project_project_1_demo')

    def _test_website_page(self, page, code=200):
        response = self.url_open(page)
        self.assertEqual(response.status_code, code)

    def test_psc_teams_page(self):
        self._test_website_page("/psc-teams")

    def test_psc_project_detail_page(self):
        self._test_website_page(
            "/psc-teams/{}".format(slug(self.test_project)))

        # It should not give an error if user changes manually
        # project id in url.
        self._test_website_page(
            "/psc-teams/{}-{}".format(self.test_project.name, 999))

        self.phantom_js("/psc-teams",
                        "odoo.__DEBUG__.services['web_tour.tour']"
                        ".run('psc_team_project_tour')",
                        "odoo.__DEBUG__.services['web_tour.tour']"
                        ".tours.psc_team_project_tour.ready",
                        login="project_manager_demo")

        cr = self.registry.cursor()
        assert cr == self.registry.test_cr
        user_id = self.env.ref(
            'website_oca_psc_team.project_manager_user_demo').id
        env = Environment(cr, user_id, {})

        app_store_project_id = self.browse_ref(
            'oca_psc_team.project_project_1_demo').id

        self.app_store_project = env['project.project'].sudo().browse(
            app_store_project_id)

        self.assertEqual(
            self.app_store_project.description,
            '<p>Updated Apps store project description.</p>'
        )
