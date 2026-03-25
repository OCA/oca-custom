# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

class ResPartnerIndustry(models.Model):
    _inherit = ["res.partner.industry"]

    sequence = fields.Integer()
    description = fields.Text(
        string="Description",
        help="The description is shared between all sponsors using this industry.",
    )
