# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class MailGroupMember(models.Model):
    _inherit = "mail.group.member"

    active = fields.Boolean(default=True)
    grace_date_start = fields.Date(
        help="Date on which the member is not legitimate anymore to belong "
        "in this Mailing",
    )
    grace_date_deadline = fields.Date(
        string="Grace Deadline",
        compute="_compute_grace_date_deadline",
        help="Date on which the member will be retired automatically from this "
        "Mailing Group, unless he/she renew its membership.",
    )

    # ===== Compute =====#
    @api.depends("grace_date_start", "mail_group_id.grace_days")
    def _compute_grace_date_deadline(self):
        for member in self:
            member.grace_date_deadline = bool(
                member.grace_date_start
            ) and member.grace_date_start + timedelta(
                days=member.mail_group_id.grace_days
            )

    # ===== CRUD =====#
    def write(self, vals):
        """When called from `_join_group`, if a user re-subscribe a previously
        unsubscribed group, re-active its membership instead of creating a duplicate"""
        if self._context.get("from_portal"):
            vals["active"] = True
        return super().write(vals)

    def unlink(self):
        """When a user leaves a group, remember its unsubscription
        (=archive instead of unlink) to avoid provisioning it automatically"""
        if self._context.get("from_portal"):
            self.with_context(from_portal=False).action_archive()
        else:
            return super().unlink()
