# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, exceptions, _
from datetime import timedelta


class MailGroupMember(models.Model):
    _inherit = ["mail.group.member"]

    active = fields.Boolean(default=True)
    grace_date_start = fields.Date(
        string="Grace Date Start",
        readonly=True,
        help="Date on which the member is not legitimate anymore to belong "
             "in this Mailing"
    )
    grace_date_deadline = fields.Date(
        string="Grace Date Deadline",
        compute="_compute_grace_date_deadline",
        help="Date on which the member will be retired automatically from this "
             "Mailing Group, unless he/she renew its membership.",
    )

    #===== Constrain =====#
    @api.constrains("mail_group_id")
    def _constrain_mail_group_ids(self):
        if self._context.get("allow_membership_provision_groups"):
            return
        members = self._get_auto_member()
        if members:
            raise exceptions.UserError(_(
                "Modifying members of the following Mail Groups cannot be done "
                "manually, because those groups follow member's roles: %s.",
                ", " . join(members.mapped("name"))
            ))

    def _get_auto_member(self):
        return self.mail_group_id.filtered("membership_category_ids")

    #===== Compute =====#
    @api.depends("grace_date_start", "mail_group_id.grace_days")
    def _compute_grace_date_deadline(self):
        for member in self:
            member.grace_date_deadline = (
                bool(member.grace_date_start) and
                member.grace_date_start + timedelta(days=member.mail_group_id.grace_day)
            )

    #===== CRUD =====#
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._constrain_mail_group_ids()
        return records

    def unlink(self):
        self._constrain_mail_group_ids()
        return super().unlink()
