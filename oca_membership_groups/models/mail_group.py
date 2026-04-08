# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

class MailGroup(models.Model):
    _inherit = ["mail.group"]
    _mailing_enabled = True # for Email Marketing (marketing_card) 

    is_working_group = fields.Boolean(
        string="Is a Working Group",
        default=False,
        help="Working Group are visible on the website page, on members profile.",
    )
    membership_category_ids = fields.Many2many(
        string="Mail Groups",
        comodel_name="membership.membership_category",
        relation="membership_category_mail_group_rel",
        column2="mail_group_id",
        column1="category_id",
        help="The members of this Mailing Group follows the members of those "
            "membership categories."
    )
    grace_days = fields.Integer(
        string="Grace Days",
        default=90,
        help="Number of days before the expired members are automatically "
             "retired from this group. Only relevant for groups with auto-subscription "
             "from the membership category.",
    )

    #===== CRUD =====#
    def write(self, vals):
        """When called from `_join_group`, if a user re-subscribe a previously
        unsubscribed group, re-active its membership instead of creating a duplicate"""
        if self._context.get("remember_unsubscribed"):
            vals["active"] = True
        return self.write(vals)

    def unlink(self):
        """When a user leaves a group, remember its unsubscription
        (=archive instead of unlink) to avoid provisioning it automatically"""
        if self._context.get("remember_unsubscribed"):
            self.active = False
        else:
            return super().unlink()

    #===== Logics =====#
    def _with_remember_unsubscribed(self):
        """Called from the portal actions. It alters native `_join_group` (via `write`)
        and `_leave_group` (via `unlink`) to archive instead of unlinking the
        members, thus remembering their explicit choice not to add them again
        i.e. archived member = explicit unsubscription"""
        return self.with_context(active_test=False, remember_unsubscribed=True)
