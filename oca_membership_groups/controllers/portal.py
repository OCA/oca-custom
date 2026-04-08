# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mail_group.controllers.portal import PortailMailGroup
from odoo.exceptions import AccessError
from odoo.http import request, Response
from odoo.osv import expression
from odoo.tools import consteq
from odoo.tools.misc import get_lang


class PortalMailGroupMembership(PortailMailGroup):
    def _group_subscription_get_group(self, group_id, email, token):
        """When user is logged, (un)subscribe the user"""
        group_sudo, is_member, partner_id = self._group_subscription_get_group(group_id, email, token)
        return (
            group_sudo._with_remember_unsubscribed(),
            is_member,
            partner_id
        )

    def _group_subscription_confirm_get_group(self, group_id, email, token, action):
        """For unlogged user, called to find group from the email link"""
        group = super()._group_subscription_confirm_get_group(group_id, email, token, action)
        return group._with_remember_unsubscribed() if group else group
