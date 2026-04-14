# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VcpRepository(models.Model):
    _inherit = "vcp.repository"

    category_id = fields.Many2one("vcp.repository.category")
