# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models


class VcpRepositoryCategory(models.Model):
    _inherit = ["vcp.repository.category", "abstract.url", "se.indexable.record"]
    _name = "vcp.repository.category"

    def _add_to_oca_search_engine(self):
        self._add_to_index(
            self.env.ref("oca_search_engine.oca_typesense_index_category")
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._add_to_oca_search_engine()
        return records

    def write(self, vals):
        self._se_mark_to_update()
        return super().write(vals)

    def _generate_url_key(self, referential, lang):
        url_key = super()._generate_url_key(referential, lang)
        return f"categories/{url_key}"
