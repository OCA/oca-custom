# Copyright 2026 Akretion (https://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api

class BlogPost(models.Model):
    """Play review process at any update of a sponsor's blog,
    except if the update is done by a reviewer"""
    _inherit = ["blog.post"]

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self.author_id._set_sponsor_to_review()
        return res

    def write(self, vals):
        res = super().write(vals)
        self.author_id._set_sponsor_to_review()
        return res
