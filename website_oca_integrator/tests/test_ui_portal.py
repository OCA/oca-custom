# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_integrator_portal(self):
        self.phantom_js("/",
                        "odoo.__DEBUG__.services['web_tour.tour']"
                        ".run('integrator_portal')",
                        "odoo.__DEBUG__.services['web_tour.tour']"
                        ".tours.integrator_portal.ready",
                        login="integrator")
