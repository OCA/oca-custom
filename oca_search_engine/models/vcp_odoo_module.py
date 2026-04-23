# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class VcpOdooModule(models.Model):
    _name = "vcp.odoo.module"
    _inherit = ["vcp.odoo.module", "abstract.url"]

    def _generate_url_key(self, referential, lang):
        url_key = super()._generate_url_key(referential, lang)
        return f"modules/{url_key}"
