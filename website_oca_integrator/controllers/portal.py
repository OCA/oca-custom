# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo import http
from odoo.http import request, route

from odoo.addons.portal.controllers.portal import CustomerPortal


class IntegratorPortal(CustomerPortal):
    OPTIONAL_BILLING_FIELDS = CustomerPortal.OPTIONAL_BILLING_FIELDS + \
        ['github_organization', 'favourite_module_ids',
            'website_short_description', 'website_description', 'files']

    @route()
    def account(self, redirect=None, **post):
        response = super(IntegratorPortal, self).account(
            redirect=redirect, **post)
        if post:
            module_list = []
            partner = request.env.user.partner_id
            modules = post.get('favourite_module_ids')
            if modules:
                module_list = map(int, modules.split(','))
            partner.sudo().write(
                {'favourite_module_ids': [(6, 0, module_list)]})
        return response

    @http.route('/my/account/get_developed_modules', type='http', auth="user",
                methods=['GET'], website=True, sitemap=False)
    def integrator_developed_module_read(self, query='', limit=25, **post):
        integrator = request.env.user.partner_id
        modules_data = request.env['product.template'].search_read(
            [('id', 'in', integrator.developed_module_ids.ids),
             ('name', '=ilike', "%" + (query or '') + "%")],
            fields=['id', 'name'], limit=int(limit))
        return json.dumps(modules_data)

    @http.route('/my/account/get_favourite_modules', type='http', auth="user",
                methods=['GET'], website=True, sitemap=False)
    def integrator_favourite_module_read(self):
        integrator = request.env.user.partner_id
        modules = integrator.favourite_module_ids
        modules_data = ([{'id': m.id, 'name': m.name} for m in modules])
        return json.dumps(modules_data)
