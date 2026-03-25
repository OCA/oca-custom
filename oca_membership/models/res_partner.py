# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = ["res.partner"]

    membership_category_id = fields.Many2one(
        comodel_name="membership.membership_category",
        string="Target role",
        help="Role for next subscribed membership",
        default=lambda self: self._default_membership_category_id(),
    )
    mail_group_member_ids = fields.One2many(
        string="Mailing list membership",
        comodel_name="mail.group.member",
        inverse_name="partner_id",
        domain=[("mail_group_id.is_working_group", "=", True)],
    )
    working_group_ids = fields.One2many(
        # UI fields
        string="Working Groups",
        comodel_name="mail.group",
        compute="_compute_working_group_ids",
        inverse="_inverse_working_group_ids",
    )

    def _default_membership_category_id(self):
        return self.env["membership.membership_category"].search([], limit=1).id

    @api.depends("mail_group_member_ids.mail_group_id")
    def _compute_working_group_ids(self):
        for partner in self:
            partner.working_group_ids = partner._get_working_groups()

    def _inverse_working_group_ids(self):
        """Create or remove membership in mail_group"""
        for partner in self:
            user_input = partner.working_group_ids
            before = partner._get_working_groups()
            added = user_input - before
            removed = before - user_input
            if added:
                for mail_group in added:
                    mail_group.sudo()._join_group(partner.email, partner.id)
            if removed:
                partner.mail_group_member_ids.filtered(
                    lambda x: x.mail_group_id in removed
                ).unlink()

    def _get_working_groups(self):
        return self.mail_group_member_ids.mail_group_id
