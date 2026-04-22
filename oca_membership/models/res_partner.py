# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = ["res.partner"]

    is_member = fields.Boolean(
        string="Member",
        help="Is currently a member of the assocation",
        compute="_compute_is_member",
        store=True,
    )
    is_integrator = fields.Boolean(
        string="Integrator",
        compute="_compute_is_integrator",
        store=True,
    )
    membership_category_id = fields.Many2one(
        comodel_name="membership.membership_category",
        string="Target role",
        help="Role for next subscribed membership",
        default=lambda self: self._default_membership_category_id(),
    )
    membership_category_ids = fields.Many2many(
        string="Active roles",
        compute="_compute_membership_state",
    )
    # Mail Groups: needed for for `oca_search_engine`,
    # rest is in `oca_membership_groups`
    mail_group_member_ids = fields.One2many(
        comodel_name="mail.group.member",
        inverse_name="partner_id",
    )
    # website privacy
    is_published = fields.Boolean(
        tracking=True,
        help="Whether this contact publicly appears on the website.\n"
        "Automatically enabled for companies (sponsors and integrators).\n"
        "To enable manually for individuals (members).",
    )
    is_published_email = fields.Boolean(string="Publish email")
    is_published_phone = fields.Boolean(string="Publish phone")
    is_published_address = fields.Boolean(string="Publish address")
    is_published_website = fields.Boolean(string="Publish website")

    def _default_membership_category_id(self):
        return self.env["membership.membership_category"].search([], limit=1).id

    # ===== Compute =====#
    @api.depends("membership_category_ids.implied_ids")
    def _compute_membership_state(self):
        """Add in `membership_category_ids` the current role and its implied roles
        Example: a 'Delegate' is also a 'Member'"""
        res = super()._compute_membership_state()
        for partner in self:
            partner.membership_category_ids |= (
                partner.membership_category_ids.implied_ids
            )
        return res

    @api.depends("membership_state")
    def _compute_is_member(self):
        member_states = self._membership_member_states()
        for partner in self:
            partner.is_member = bool(partner.membership_state in member_states)

    @api.depends(
        "child_ids",
        "child_ids.is_member",
        "child_ids.parent_id",
        "child_ids.vcp_user_ids",
    )
    def _compute_is_integrator(self):
        """Integrators are companies having contributors or members"""
        for partner in self:
            partner.is_integrator = partner.is_company and any(
                child._is_contributor() or child.is_member
                for child in partner.child_ids
            )

    # ===== Logics =====#
    def _is_contributor(self):
        """Partner with any commit, pull request or message on Github"""
        return bool(self.vcp_user_ids)
