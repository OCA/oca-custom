# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, exceptions, _

class BlogPost(models.Model):
    _inherit = ["blog.post"]

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)._refresh_sponsor_search_engine()

    def write(self, vals):
        res = super().write(vals)
        self._refresh_sponsor_search_engine()
        return res
    
    def _refresh_sponsor_search_engine(self):
        self.author_id._add_to_oca_search_engine()
        return self

    def _get_background_url(self):
        """Strips the css and returns background's absolute URL"""
        background_image = (self._get_background() or '')
        if not background_image or background_image == "none":
            return None
        elif background_image.startswith("url(/web/image/"):
            return self.get_base_url() + background_image[4:-1]
        else:
            return background_image
