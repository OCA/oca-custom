# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class VcpOdooModuleVersion(models.Model):
    _inherit = "vcp.odoo.module.version"

    readme_fragments = fields.Json()
    icon_url = fields.Char()
