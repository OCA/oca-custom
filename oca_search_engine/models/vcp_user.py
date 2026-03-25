# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models, fields


class VcpUser(models.Model):
    _inherit = ["vcp.user"]

    vcp_oca_psc_ids = fields.Many2many(
        comodel_name="vcp.oca.psc",
        relation="vcp_oca_psc_user_rel",
        column1="user_id",
        column2="team_id",
    )
