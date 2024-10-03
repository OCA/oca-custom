# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from datetime import date
import base64
import json
from odoo import fields
from odoo.tests.common import TransactionCase


class TestOcaMonetize(TransactionCase):
    def test_subscription(self):
        """First line of docstring appears in test logs.

        Other lines do not.

        Any method starting with ``test_`` will be tested.
        """
        self.assertFalse(self.env['oca.monetize']._get_subscription())
        self.env['ir.config_parameter'].set_param(
            'oca_monetize.name', 'Hunki Enterprises BV',
        )
        version = '1.0'
        partner_name = "Hunki Enterprises BV"
        start_date = fields.Datetime.to_string(date.today().replace(month=1, day=1))
        end_date = fields.Datetime.to_string(date.today().replace(month=12, day=31))
        subscription = dict(version=version, start_date=start_date, end_date=end_date, partner_name=partner_name)
        self.env['ir.config_parameter'].set_param(
            'oca_monetize.key', base64.b64encode((json.dumps(subscription)).encode('utf8')).decode('utf8'),
        )
        self.assertTrue(self.env['oca.monetize']._get_subscription())
