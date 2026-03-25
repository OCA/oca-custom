# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# Copyright 2026 Akretion (https://akretion.com)
# > moved from `website_oca_integrator` in v18.0 (2026-03)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SponsorshipLine(models.Model):
    _name = "sponsorship.line"
    _description = "Sponsorship history"

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    date_from = fields.Date(string="Join Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    grade_id = fields.Many2one(
        comodel_name="res.partner.grade",
        string="Sponsor Level",
        required=True,
    )
