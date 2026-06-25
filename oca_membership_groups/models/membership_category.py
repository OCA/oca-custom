# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MembershipCategory(models.Model):
    _inherit = "membership.membership_category"

    mail_group_ids = fields.Many2many(
        string="Mail Groups",
        comodel_name="mail.group",
        relation="membership_category_mail_group_rel",
        column1="category_id",
        column2="mail_group_id",
        help="The members of this category will automatically subscribe to these "
        "Mail Groups. They will be able to unsubscribe too.",
    )
