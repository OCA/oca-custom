# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailGroupMember(models.Model):
    """Refresh partners data on the Search Engine
    when added/removed to a Working Group"""

    _inherit = "mail.group.member"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._se_update_partners()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._se_update_partners()
        return res

    def unlink(self):
        partner = self.partner_id
        res = super().unlink()
        partner.sudo()._se_mark_to_update()
        return res

    def _se_update_partners(self):
        wg_members = self.filtered(lambda x: x.mail_group_id.is_working_group)
        wg_members.sudo().partner_id._se_mark_to_update()
