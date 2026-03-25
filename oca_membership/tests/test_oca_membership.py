# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, new_test_user, users


class TestOcaMembership(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
