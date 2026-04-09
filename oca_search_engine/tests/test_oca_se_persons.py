# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase

from ..schemas.res_partner_person import Person


class TestOcaPersonsSearchEngine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.member = cls.env["res.partner"].create(
            [
                {
                    "name": "Happy Member",
                    "is_company": False,
                    "country_id": cls.env.ref("base.fr").id,
                    "is_published": True,
                }
            ]
        )

    def test_persons_json_output(self):
        """Test output generation methods: very simple tests,
        just to ensure the code does not throw errors"""
        data = Person.from_record(self.member).model_dump(mode="json")
        self.assertEqual(data["country"]["code"], "FR")
