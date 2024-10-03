# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from datetime import date
import json
import base64
from odoo import api, fields, models, tools


class OcaMonetize(models.AbstractModel):
    _name = "oca.monetize"

    @api.model
    def has_valid_subscription(self):
        # hello reader, you've found the spot where you can deactivate the
        # nagging for a subscription easily.
        # there's no way to detain you from doing so, but before going ahead
        # please consider the high value you get from oca, and that this
        # needs to be financed somehow. if there are too many people dodging
        # contributing, the whole thing collapses
        return bool(self._get_subscription())

    @api.model
    def _get_subscription(self, enforce_valid=True):
        ResConfigSettings = self.env['res.config.settings']
        try:
            name = self.env['ir.config_parameter'].sudo().get_param(
                ResConfigSettings._fields['oca_monetize_name'].config_parameter, '',
            )
            subscription = json.loads(base64.b64decode(self.env['ir.config_parameter'].sudo().get_param(
                ResConfigSettings._fields['oca_monetize_key'].config_parameter, '',
            )))
            subscription['version'] = tools.parse_version(subscription['version'])
            subscription['start_date'] = fields.Date.from_string(subscription['start_date'])
            subscription['end_date'] = fields.Date.from_string(subscription['end_date'])
            if not enforce_valid:
                return subscription
            if subscription['partner_name'] != name:
                return {}
            if subscription['start_date'] >= date.today() or subscription['end_date'] <= date.today():
                return {}
            return subscription
        except:
            
            return {}
