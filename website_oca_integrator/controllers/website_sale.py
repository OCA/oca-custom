# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# Part of Odoo. See Odoo LICENSE file for full copyright and licensing details.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request

from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute

PPG = 40  # Products Per Page
PPR = 4   # Products Per Row


class WebsiteIntegratorSale(WebsiteSale):

    def get_product_per_page(self, ppg=False, **post):
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        return ppg, post

    @http.route()
    def shop(self, page=0, category=None, search='', integrator='', ppg=False,
             **post):
        """
        Filter products by integrator.
        """
        response = super(WebsiteIntegratorSale, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)

        # execute below block if url contains integrator parameter
        if integrator:
            _, integrator_id = unslug(integrator)
            integrator = request.env['res.partner'].sudo().browse(
                integrator_id).exists()
            if integrator:
                ppg, post = self.get_product_per_page(ppg, **post)
                attrib_values = response.qcontext['attrib_values']
                attrib_list = request.httprequest.args.getlist('attrib')

                product = request.env['product.template']

                url = "/shop"
                if search:
                    post["search"] = search
                if category:
                    category = request.env['product.public.category'].browse(
                        int(category))
                    url = "/shop/category/%s" % slug(category)
                if attrib_list:
                    post['attrib'] = attrib_list
                post["integrator"] = integrator_id

                domain = self._get_search_domain(
                    search, category, attrib_values)
                domain += [('id', 'in', integrator.developed_module_ids.ids)]

                product_count = product.search_count(domain)

                pager = request.website.pager(
                    url=url, total=product_count, page=page, step=ppg,
                    scope=7, url_args=post)

                products = product.search(domain, limit=ppg,
                                          offset=pager['offset'],
                                          order=self._get_search_order(post))

                keep = QueryURL('/shop',
                                category=category and int(category),
                                search=search, integrator=slug(integrator),
                                attrib=attrib_list, order=post.get('order'))

                values = {
                    'products': products,
                    'bins': TableCompute().process(products, ppg),
                    'pager': pager,
                    'search_count': product_count,
                    'search': search,
                    'integrator': integrator,
                    'keep': keep,
                }
                response.qcontext.update(values)
                return response

        return response
