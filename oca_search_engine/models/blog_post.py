# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class BlogPost(models.Model):
    _inherit = "blog.post"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.author_id._se_mark_to_update()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.author_id._se_mark_to_update()
        return res

    def _get_background_url(self):
        """Strips the css and returns background's absolute URL"""
        background_image = self._get_background() or ""
        if not background_image or background_image == "none":
            return None
        elif background_image.startswith("url(/web/image/"):
            return self.get_base_url() + background_image[4:-1]
        else:
            return background_image
