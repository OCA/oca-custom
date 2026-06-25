# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    mail_group_member_ids = fields.One2many(
        comodel_name="mail.group.member",
        inverse_name="partner_id",
    )
    mail_group_count = fields.Integer(
        string="Mail Groups",
        compute="_compute_mail_group_count",
    )

    # ===== Compute =====#
    @api.depends("mail_group_member_ids")
    def _compute_mail_group_count(self):
        for partner in self:
            partner.mail_group_count = len(partner.mail_group_member_ids)

    def _compute_membership_state(self):
        """Update Mail Groups according to changes in Membership Categories"""
        res = super()._compute_membership_state()
        if not isinstance(self.id, models.NewId):
            self._membership_groups_refresh()
        return res

    # ===== Logics =====#
    def _join_mail_groups(self, groups):
        """Add member to groups unless they unsubscribed* before
        (*archived membership)"""
        if not groups:
            return
        self.ensure_one()
        subscribed_group_ids = list(
            (
                groups.with_context(active_test=False)._find_members(
                    self.email, self.id
                )
            ).keys()
        )
        new_groups = groups.filtered(lambda x: x.id not in subscribed_group_ids)
        for group in new_groups:
            group._join_group(self.email, self.id)

    def _leave_mail_groups(self, groups):
        """Unlink the membership unless the member explicitely unsubscribed.
        In latter case, `_leave_group` will keep the subscription since it's
        archived."""
        self.ensure_one()
        for group in groups:
            group._leave_group(self.email, self.id)

    def _toggle_grace_mail_groups(self, groups, grace_date_start):
        """Stop grace if `grace_date_start=False`
        Start grace if `grace_date_start` is defined"""
        if not groups:
            return
        self.ensure_one()

        members = self.mail_group_member_ids.filtered(
            lambda x: x.mail_group_id in groups
        )
        if grace_date_start:
            members = members.filtered(lambda x: not x.grace_date_start)
        else:
            members = members.filtered("grace_date_start")
        members.grace_date_start = grace_date_start

    def _membership_groups_refresh(self):
        """Auto-add members in Mailing Groups, and start or stop grace period,
        according to their membership's category and implied Mailing Groups"""
        today = fields.Date.today()
        for partner in self:
            # Add the member to new groups and stop any grace period previously set
            joined_groups = partner.membership_category_ids.mail_group_ids
            partner._join_mail_groups(joined_groups)
            partner._toggle_grace_mail_groups(joined_groups, False)

            # Start grace period of the leaving membership groups
            current_groups = partner.mail_group_member_ids.mail_group_id
            leaving_groups = (current_groups - joined_groups).filtered(
                "membership_category_ids"
            )
            partner._toggle_grace_mail_groups(leaving_groups, today)

        # For groups with grace_days=0, remove members immediatly
        self._membership_groups_end_grace()

    @api.model
    def _cron_membership_groups_end_grace(self):
        self._membership_groups_end_grace()

    @api.model
    def _membership_groups_end_grace(self):
        """End grace periods (remove expired mail group's members)"""
        today = fields.Date.today()
        partners = self.env["res.partner"].search([])
        expired_members_grouped = partners.mail_group_member_ids.filtered(
            lambda x: x.grace_date_start and today >= x.grace_date_deadline
        ).grouped("partner_id")
        for partner, expired_members in expired_members_grouped.items():
            partner._leave_mail_groups(expired_members.mail_group_id)

    # ===== Mailing =====#
    def _mailing_get_default_domain(self, _):
        """Email Martketing: default domain to fetch for Members"""
        categories = self.env["membership.membership_category"].search([])
        return [
            ("membership_state", "in", self._membership_member_states()),
            ("membership_category_id", "in", categories.ids),
        ]
