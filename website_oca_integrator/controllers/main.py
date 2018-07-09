# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import werkzeug

from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.tools.translate import _


class WebsiteIntegrator(http.Controller):
    _references_per_page = 40

    @http.route([
        '/integrators',
        '/integrators/page/<int:page>',

        '/integrators/country/<model("res.country"):country>',
        '/integrators/country/<model("res.country"):country>/page/<int:page>',
    ], type='http', auth="public", website=True)
    def integrators(self, country=None, page=0, **post):
        """
        Displays integrators in website.
        """
        country_all = post.pop('country_all', False)
        partner_obj = request.env['res.partner']
        search = post.get('search', '')

        # serch integrators
        base_integrator_domain = [('is_company', '=', True),
                                  ('is_integrator', '=', True),
                                  ('website_published', '=', True)]

        if search:
            base_integrator_domain += ['|', ('name', 'ilike', search),
                                       ('website_description', 'ilike',
                                        search)]

        # group by country
        country_domain = list(base_integrator_domain)
        countries = partner_obj.sudo().read_group(
            country_domain, ["id", "country_id"],
            groupby="country_id", orderby="country_id")
        countries_partners = partner_obj.sudo().search_count(
            country_domain)

        # flag active country
        for country_dict in countries:
            country_dict['active'] = country and country_dict['country_id'] \
                and country_dict['country_id'][
                0] == country.id
        countries.insert(0, {
            'country_id_count': countries_partners,
            'country_id': (0, _("All Countries")),
            'active': bool(country is None),
        })

        if country:
            base_integrator_domain += [('country_id', '=', country.id)]
            url = '/integrators/country/' + slug(country)
        else:
            url = '/integrators'

        url_args = {}
        if search:
            url_args['search'] = search
        if country_all:
            url_args['country_all'] = True

        partner_count = partner_obj.sudo().search_count(base_integrator_domain)
        pager = request.website.pager(
            url=url,
            total=partner_count,
            page=page,
            step=self._references_per_page,
            scope=7,
            url_args=url_args)

        # search integrators matching current search parameters
        integrator_ids = partner_obj.sudo().search(
            base_integrator_domain, order="grade_id DESC, display_name ASC",
            offset=pager['offset'], limit=self._references_per_page)
        integrators = integrator_ids.sudo()

        google_map_partner_ids = ','.join(
            map(str, [i.id for i in integrators]))
        google_maps_api_key = request.env['ir.config_parameter'].sudo(
        ).get_param('google_maps_api_key')

        values = {
            'countries': countries,
            'current_country': country,
            'integrators': integrators,
            'google_map_integrator_ids': google_map_partner_ids,
            'pager': pager,
            'searches': post,
            'search_path': "%s" % werkzeug.url_encode(post),
            'google_maps_api_key': google_maps_api_key,
        }

        return request.render(
            "website_oca_integrator.index",
            values,
            status=integrators and 200 or 404)
