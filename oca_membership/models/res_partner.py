# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _

class ResPartner(models.Model):
    _inherit = ["res.partner"]

    is_member = fields.Boolean(
        string="Is currently a member",
        compute="_compute_is_member",
        search="_search_is_member",
    )
    membership_category_id = fields.Many2one(
        comodel_name="membership.membership_category",
        string="Target role",
        help="Role for next subscribed membership",
        default=lambda self: self._default_membership_category_id(),
    )
    membership_category_ids = fields.Many2many(
        string="Active roles",
        # `_compute_membership_state` is inherited too
    )
    mail_group_member_ids = fields.One2many(
        comodel_name="mail.group.member",
        inverse_name="partner_id",
    )

    def _default_membership_category_id(self):
        return self.env["membership.membership_category"].search([], limit=1).id

    #===== Compute =====#
    @api.depends("membership_category_ids.implied_ids")
    def _compute_membership_state(self):
        """Change `membership_category_ids` so it displays current role
        plus implied roles, e.g. a 'Delegate' is also a 'Member'
        (for the website, and the backend)"""
        res = super()._compute_membership_state()
        for partner in self:
            partner.membership_category_ids |= partner.membership_category_ids.implied_ids
        return res
    
    @api.depends("membership_state")
    def _compute_is_member(self):
        member_states = self._membership_member_states()
        for partner in self:
            partner.is_member = bool(partner.membership_state in member_states)
    @api.model
    def _search_is_member(self, operator, value):
        if operator not in ('=', '!=') or not isinstance(value, bool):
            raise NotImplementedError(_("Operation not supported."))
        operator = (
            "in"
            if operator == "=" and value or not operator == "!=" and not value
            else "not in"
        )
        return [('membership_state', operator, self._membership_member_states())]

    #===== Business logics =====#
    def _get_working_groups(self):
        """For `oca_search_engine"""
        return self.mail_group_member_ids.mail_group_id.filtered("is_working_group")

    def _get_company_members(self):
        """Members of a company"""
        return self.filtered("is_company").child_ids.filtered("is_member")
