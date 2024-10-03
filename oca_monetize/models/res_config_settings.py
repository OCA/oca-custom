# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class OcaMonetize(models.TransientModel):
    _inherit = "res.config.settings"

    oca_monetize_name = fields.Char('Partner Name', config_parameter='oca_monetize.name')
    oca_monetize_key = fields.Char('Subscription Key', config_parameter='oca_monetize.key')
