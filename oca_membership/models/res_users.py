# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResUsers(models.Model):
    """Refresh the `res.group` 'Membership: members'
    when the `res.user` of a member is created *after* the `res.partner`,
    like in the process of membership paid by the company
    """

    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        users.partner_id._membership_groups_refresh()
        return users

    def write(self, vals):
        res = super().write(vals)
        if "partner_id" in vals:
            self.partner_id._membership_groups_refresh()
        return res
