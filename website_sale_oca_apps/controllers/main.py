# Copyright 2026 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import werkzeug.utils
from werkzeug.urls import url_join

from odoo import http
from odoo.http import request

from odoo.addons.website_partner.controllers.main import WebsitePartnerPage
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleProductRedirect(WebsiteSale):
    @http.route()
    def product(self, product, category="", search="", **kwargs):
        product_sudo = product.sudo()
        if not product_sudo.active and not product_sudo.is_published:
            new_shop_url = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "website_oca_apps_new_shop.url", "https://apps.odoo-community.org"
                )
            )
            url = (
                request.env["url.url"]
                .sudo()
                .search([("key", "=", product_sudo.website_url)])
            )
            if url:
                url_key = (
                    request.env["vcp.odoo.module"].sudo().browse(url.res_id).url_key
                )
                product_url = url_join(new_shop_url, url_key)
                return werkzeug.utils.redirect(product_url, 301)
        return super().product(product, category=category, search=search, **kwargs)


class WebsitePartnerPageRedirect(WebsitePartnerPage):
    @http.route(
        [
            "/partners/<partner_id>",
            "/integrators/<partner_id>",
        ],
        type="http",
        auth="public",
        website=True,
    )
    def partners_detail(self, partner_id, **post):
        _, partner_id = request.env["ir.http"]._unslug(partner_id)
        if partner_id:
            partner_sudo = request.env["res.partner"].sudo().browse(partner_id)
            if partner_sudo.is_sponsor:
                new_shop_url = (
                    request.env["ir.config_parameter"]
                    .sudo()
                    .get_param(
                        "website_oca_apps_new_shop.url",
                        "https://apps.odoo-community.org",
                    )
                )
                if partner_sudo.url_key:
                    url = url_join(new_shop_url, partner_sudo.url_key)
                    return werkzeug.utils.redirect(url, 301)
        return super().partners_detail(partner_id, **post)


class WebsiteMembership(http.Controller):
    # Do not use semantic controller due to SUPERUSER_ID
    @http.route(["/members/<partner_id>"], type="http", auth="public", website=True)
    def partners_detail(self, partner_id, **post):
        _, partner_id = request.env["ir.http"]._unslug(partner_id)
        if partner_id:
            partner_sudo = request.env["res.partner"].sudo().browse(partner_id)
            if partner_sudo.exists() and partner_sudo.website_published:
                new_shop_url = (
                    request.env["ir.config_parameter"]
                    .sudo()
                    .get_param(
                        "website_oca_apps_new_shop.url",
                        "https://apps.odoo-community.org",
                    )
                )
                if partner_sudo.url_key:
                    url = url_join(new_shop_url, partner_sudo.url_key)
                    return werkzeug.utils.redirect(url, 301)
        raise request.not_found()
