# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

class MembershipCategory(models.Model):
    _inherit = ["membership.membership_category"]
    _description = "Membership role"
    _order = "sequence"

    sequence = fields.Integer("Sequence")
    implied_ids = fields.Many2many(
        string="Implied roles",
        comodel_name="membership.membership_category",
        relation="membership_category_implied_rel",
        column1="category_id",
        column2="implied_category_id",
        help="Implied roles by this one",
    )
