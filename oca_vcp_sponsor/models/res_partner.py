# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_organization(self, date):
        partner = super()._get_organization(date)
        return partner.sponsor_parent_id or partner
