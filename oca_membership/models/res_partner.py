# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from functools import partial

from odoo import SUPERUSER_ID, Command, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_member = fields.Boolean(
        string="Member",
        help="Is currently a member of the assocation",
        compute="_compute_is_member",
        store=True,
    )
    is_elected = fields.Boolean(
        string="Elected",
        compute="_compute_is_elected",
        search="_search_is_elected",
    )
    is_contributor = fields.Boolean(
        string="Contributor",
        help="Has participated in Github, with a comment, a commit, ...",
        compute="_compute_is_contributor",
        store=True,
    )
    is_integrator = fields.Boolean(
        string="Integrator",
        compute="_compute_is_integrator",
        store=True,
    )
    membership_category_id = fields.Many2one(
        comodel_name="membership.membership_category",
        string="Current category",
        default=lambda self: self._get_default_membership_category().id,
        help="This field may reflect a Role in the association. Changing it is "
        "immediatly reflected on Membership Categories.",
    )
    membership_category_ids = fields.Many2many(
        compute="_compute_membership_state",
        help="Categories of active membership lines plus Current Category.",
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

    @api.model
    def _get_default_membership_category(self):
        return self.env["membership.membership_category"].search([], limit=1)

    @api.model
    def _membership_member_states(self):
        """Inherit to only consider members the ones with 'paid' membership
        (and remove 'invoiced')"""
        return ("paid",)

    # ===== Compute =====#
    @api.depends("membership_state")
    def _compute_is_member(self):
        member_states = self._membership_member_states()
        for partner in self:
            partner.is_member = bool(partner.membership_state in member_states)

    @api.depends("is_member")
    def _compute_is_elected(self):
        default_category = self._get_default_membership_category()
        for partner in self:
            partner.is_elected = (
                partner.membership_category_id
                and partner.membership_category_id != default_category
            )

    @api.model
    def _search_is_elected(self, operator, value):
        if operator != "=" or not isinstance(value, bool) or not value:
            raise NotImplementedError()

        default_category = self._get_default_membership_category()
        return [
            ("membership_category_id", "not in", [False, default_category.id]),
        ]

    @api.depends("vcp_user_ids")
    def _compute_is_contributor(self):
        for partner in self:
            partner.is_contributor = bool(partner.vcp_user_ids)

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
                child.is_contributor or child.is_member for child in partner.child_ids
            )

    @api.depends(
        "membership_category_id",
        "membership_category_ids.implied_ids",
    )
    def _compute_membership_state(self):
        """Add in `membership_category_ids` the current role and its implied roles
        Example: a 'Delegate' is also a 'Member'"""
        res = super()._compute_membership_state()

        for partner in self:
            categories = partner.membership_category_ids
            if partner.is_member and partner.membership_category_id:
                categories |= partner.membership_category_id
            partner.membership_category_ids = categories | categories.implied_ids

        rec_first = fields.first(self)
        if not isinstance(rec_first.id, models.NewId) or not rec_first._origin.id:
            self._membership_groups_refresh()

        return res

    # ===== Logics =====#
    def _membership_groups_refresh(self):
        """Update the group "Membership: members" with members' users.
        This is used in E-Learning module, field "Auto-Enroll Groups", for
        the access control of e-learning documents.
        Note: it will mainly be *portal* users.
        """
        group = self.env.ref("oca_membership.group_membership_member")
        if not group:
            return
        add_users = self.filtered("is_member").user_ids
        remove_users = self.user_ids - add_users
        if add_users or remove_users:
            # **Sit on your chair**
            # Writing in `res.groups` always trigger the method
            # `call_cache_clearing_methods`, which invalidates all cache
            # -> thus re-trigger `_compute_membership_state`
            # -> thus make **INFINITE LOOP**
            # To avoid it: write in `res.groups` AFTER the flush, using `postcommit`
            def update_res_group(group_id, add_user_ids, remove_user_ids):
                """This is performed in a separate transaction to allow running
                as post-commit hook"""
                with self.env.registry.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    env["res.groups"].browse(group_id).users = [
                        Command.link(x) for x in add_user_ids
                    ] + [Command.unlink(x) for x in remove_user_ids]

            self.env.cr.postcommit.add(
                partial(
                    update_res_group,
                    group.id,
                    add_users.ids,
                    remove_users.ids,
                )
            )
