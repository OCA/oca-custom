# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SponsorshipLine(models.Model):
    _name = "sponsorship.line"
    _description = "Sponsorship Line"

    date_from = fields.Date(string="Join Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    sponsorship_id = fields.Many2one(
        comodel_name="product.product", string="Sponsorship Product"
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    grade_id = fields.Many2one(
        comodel_name="res.partner.grade", string="Level", required=True
    )
