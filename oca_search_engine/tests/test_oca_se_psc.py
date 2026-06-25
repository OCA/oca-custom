# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.oca_vcp.tests.test_oca_vcp_psc import TestOcaPscsSearchEngine

from ..schemas.res_partner_person import Person
from ..schemas.vcp_oca_psc import Psc


class TestOcaPscsSearchEngine(TestOcaPscsSearchEngine):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_psc_json_output(self):
        """Test simple output for `Psc` index"""
        # Test PSC output data sent to search engine
        psc = self._process_rule_oca_psc_update()
        data = Psc.from_record(psc).model_dump(mode="json")
        self.assertEqual(data["description"], "Human name of the test OCA PSC")

    def test_person_output_psc(self):
        """Test `res.partner` membership in PSC team"""
        self._process_rule_oca_psc_update()
        user = self.env["vcp.user"].search([("name", "=", "user-github-login")])
        pscs = self.env["vcp.oca.psc"].search([])

        # 2. Test 'Person' output
        self.member.vcp_user_ids = user
        data = Person.from_record(self.member).model_dump(mode="json")
        self.assertEqual(data["psc_list"], pscs.read(["name", "description"]))
