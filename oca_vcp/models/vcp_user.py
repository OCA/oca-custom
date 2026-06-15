# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class VcpUser(models.Model):
    _inherit = "vcp.user"

    is_github_main_login = fields.Boolean()

    _sql_constraints = [
        (
            "is_github_main_login_uniq",
            "unique(is_github_main_login, partner_id)",
            "Partner can have only one github main login.",
        )
    ]
