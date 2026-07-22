# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MailGroup(models.Model):
    _inherit = "mail.group"

    def write(self, vals):
        """Refresh partners data on the Search Engine
        when a Mail Group is promoted/destituted a Working Group"""
        res = super().write(vals)
        if "is_working_group" in vals:
            self.sudo().member_ids.partner_id._se_mark_to_update()
        return res
