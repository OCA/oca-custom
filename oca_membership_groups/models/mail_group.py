# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailGroup(models.Model):
    _inherit = "mail.group"

    is_working_group = fields.Boolean(
        string="Is a Working Group",
        default=False,
        help="Working Group are visible on the website page, on members profile.",
    )
    membership_category_ids = fields.Many2many(
        string="Membership Categories",
        comodel_name="membership.membership_category",
        relation="membership_category_mail_group_rel",
        column1="mail_group_id",
        column2="category_id",
        help="The members of this Mailing Group follows the members of those "
        "membership categories.",
    )
    grace_days = fields.Integer(
        default=90,
        help="Number of days before the expired members are automatically "
        "retired from this group. Only relevant for groups with auto-subscription "
        "from the membership category.",
    )

    # ===== Logics =====#
    def _find_members(self, email, partner_id):
        """Prevent raising member constrain 'unique_partner' per mail.group"""
        return super(
            MailGroup,
            self.with_context(active_test=False),
        )._find_members(email, partner_id)
