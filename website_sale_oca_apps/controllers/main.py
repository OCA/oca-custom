# Copyright 2026 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import werkzeug.utils
from werkzeug.urls import url_join

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleProductRedirect(WebsiteSale):
    @http.route()
    def product(self, product, category="", search="", **kwargs):
        if not product.active and not product.is_published:
            new_shop_url = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "website_oca_apps_new_shop.url", "https://apps.odoo-community.org"
                )
            )
            product_url = url_join(new_shop_url, product.website_url)
            return werkzeug.utils.redirect(product_url, 307)
        return super().product(product, category=category, search=search, **kwargs)
