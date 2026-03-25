# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import os
from pathlib import Path

from odoo.tests.common import TransactionCase
from ..schemas import Person


class TestOcaPersonsSearchEngine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.member = cls.env["res.partner"].create([{
            "name": "Happy Member",
            "is_company": False,
            "country_id": cls.env.ref("base.fr").id,
            "free_member": True,
            "is_published": True,
        }])


    def test_persons_json_output(self):
        """Test output generation methods: very simple tests,
        just to ensure the code does not throw errors"""
        self.assertEqual(self.member.membership_state, "free")
        data = Person.from_record(self.member).model_dump(mode="json")

        # Test few simple data
        category_member = self.env.ref("membership_extension.membership_category_member")
        self.assertEqual(data["country"]["code"], "FR")
        self.assertEqual(
            data["roles"],
            category_member.read(["name"])
        )
