# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class VcpOrganizationHistory(models.Model):
    _name = "vcp.organization.history"
    _description = "Vcp Organization History"
    _order = "partner_id, date_start desc"

    date_start = fields.Date(required=True)
    partner_id = fields.Many2one("res.partner", required=True)
    partner_organization_id = fields.Many2one(
        "res.partner", "Organization", required=True
    )
