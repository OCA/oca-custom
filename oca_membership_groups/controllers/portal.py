# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mail_group.controllers.portal import PortalMailGroup


class PortalMailGroupMembership(PortalMailGroup):
    """Below actions are called from the portal.
    The context key alters native `_join_group` (via `write`)
    and `_leave_group` (via `unlink`) to **archive** `mail.group.member` instead
    of unlinking them, thus remembering their explicit choice of unsubscription.
    It helps not to add them again, unless they explicitely re-subscribe.
    i.e. archived member = explicit unsubscription"""

    def _group_subscription_get_group(self, group_id, email, token):
        """When user is logged, (un)subscribe the user"""
        group_sudo, is_member, partner_id = super()._group_subscription_get_group(
            group_id, email, token
        )
        return (group_sudo.with_context(from_portal=True), is_member, partner_id)

    def _group_subscription_confirm_get_group(self, group_id, email, token, action):
        """For unlogged user, called to find group from the email link"""
        group = super()._group_subscription_confirm_get_group(
            group_id, email, token, action
        )
        return group.with_context(from_portal=True) if group else group
