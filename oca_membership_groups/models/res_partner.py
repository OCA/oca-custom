# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, exceptions, tools, _

BATCH_SIZE_PROVISION_CRON = 1000

class ResPartner(models.Model):
    _inherit = ["res.partner"]

    mail_group_member_ids = fields.One2many(
        comodel_name="mail.group.member",
        inverse_name="partner_id",
    )
    mail_group_ids = fields.Many2many(
        comodel_name="mail.group",
        compute="_compute_mail_group_ids",
        # inverse="_inverse_mail_group_ids",
    )

    #===== Compute =====#
    @api.depends("mail_group_member_ids")
    def _compute_mail_group_ids(self):
        for partner in self:
            partner.mail_group_ids = partner.mail_group_member_ids.mail_group_id

    # Commented: only in readonly
    # def _inverse_mail_group_ids(self):
    #     """Add or remove Member into Mailing Groups => create/remove `mail.group.member`"""
    #     for partner in self:
    #         added = partner.mail_group_ids - partner._origin.mail_group_ids
    #         removed = partner._origin.mail_group_ids - partner.mail_group_ids
    #         partner._join_mail_groups(added)
    #         partner._leave_mail_groups(removed)

    #===== CRUD =====#
    def write(self, vals):
        res = super().write(vals)
        if "membership_category_ids" in vals:
            self._membership_provision_groups()
        return res

    def _cron_membership_provision_groups(self):
        partners = self.env["res.partner"].search([
            '|',
            ("mail_group_member_ids", "!=", False),
            ("membership_category_ids.mail_group_ids", "!=", False),
        ])
        partners_count, progress_done = len(partners), 0
        for batch_partners in tools.split_every(BATCH_SIZE_PROVISION_CRON, partners):
            batch_partners._membership_provision_groups()
        
            # In case of issue, better to void the cache and commit what is already done
            # to avoid running several times on same records in case of issue
            progress_done += len(batch_partners)
            self.env['ir.cron']._notify_progress(
                done=progress_done, remaining=partners_count - progress_done
            )
            self._cr.commit()
            self.env.invalidate_all()

    #===== Logics =====#
    def _join_mail_groups(self, groups):
        """Add member to groups unless they unsubscribed* before (*archived membership)"""
        if not groups:
            return
        self.ensure_one()

        res = groups.with_context(active_test=False)._find_members(self.email, self.id)
        for group in groups.filtered(lambda x: x.id not in res):
            group._join_group(self.email, self.id)

    def _leave_mail_groups(self, groups):
        """Unlink the membership unless the member explicitely unsubscribed.
        In latter case, keep the subscription in archived mode."""
        if not groups:
            return
        self.ensure_one()

        members = groups.with_context(active_test=False)._find_members(self.email, self.id)
        members_unsubscribed = members.filtered(lambda x: not x.active)
        if members_unsubscribed:
            raise exceptions.UserError(_(
                "The member %(member)s has already unsubscribed from the groups "
                "%(groups)s. To remember the member's choice, its membership is "
                "kept in unactive state.",
                member=self.display_name,
                groups=members_unsubscribed.mail_group_id.mapped("name"),
            ))

        for group in groups:
            group._leave_group(self.email, self.id)

    def _set_groups_grace_date(self, groups, grace_date_start):
        """Either start the grace period of a group's member,
        or stop it with `grace_date_start=False`"""
        if not groups:
            return
        self.ensure_one()

        _filter = lambda x: not x.grace_date_start if grace_date_start else "grace_date_start"
        members = groups._find_members(self.email, self.id)
        members.filtered(_filter).grace_date_start = grace_date_start

    def _membership_provision_groups(self):
        """Auto-add/remove members in Mailing Groups according their Roles in the
        association, allowing for a grace period"""
        today = fields.Date.today()
        self = self.with_context(allow_membership_provision_groups=True)
        for partner in self:
            # Add the member to new groups and stop any grace period previously set on them
            joined_groups = partner.membership_category_ids.mail_group_ids
            partner._join_mail_groups(joined_groups)
            partner._set_groups_grace_date(joined_groups, False)

            # Start grace period of the leaving groups
            current_groups = partner.mail_group_member_ids.mail_group_id
            leaving_groups = current_groups - joined_groups
            partner._set_groups_grace_date(leaving_groups, today)
            members = leaving_groups._find_members(partner.email, partner.id)
            members.filtered(lambda x: not x.grace_date_start).grace_date_start = today

            # Quit groups of finished grace period
            expired_members = partner.mail_group_member_ids.filtered(
                lambda x: today >= x.grace_date_deadline
            )
            partner._leave_mail_groups(expired_members.mail_group_id)
