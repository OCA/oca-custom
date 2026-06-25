# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import randint

from odoo import fields, models


class MembershipCategory(models.Model):
    _inherit = "membership.membership_category"
    _description = "Membership role"
    _order = "sequence"

    sequence = fields.Integer(
        help="First category will the default one for new members.",
    )
    color = fields.Integer(
        default=lambda x: randint(1, 11),
    )
    implied_ids = fields.Many2many(
        string="Implied roles",
        comodel_name="membership.membership_category",
        relation="membership_category_implied_rel",
        column1="category_id",
        column2="implied_category_id",
        help="Implied roles by this one",
    )
