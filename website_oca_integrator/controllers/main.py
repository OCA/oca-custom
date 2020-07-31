# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# Part of Odoo. See Odoo LICENSE file for full copyright and licensing details.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import werkzeug

from odoo import http
from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.http_routing.models.ir_http import slug, unslug


class WebsiteIntegrator(http.Controller):
    _references_per_page = 40

    @http.route(
        [
            "/integrators",
            "/integrators/page/<int:page>",
            '/integrators/country/<model("res.country"):country>',
            '/integrators/country/<model("res.country"):country>/page/<int:page>',
        ],
        type="http",
        auth="public",
        website=True,
    )
    def integrators(self, country=None, page=0, **post):
        """
        Display integrators in website.
        """
        country_all = post.pop("country_all", False)
        partner_obj = request.env["res.partner"]
        search = post.get("search", "")

        # search integrators
        base_integrator_domain = [
            ("is_company", "=", True),
            ("is_integrator", "=", True),
            ("website_published", "=", True),
        ]

        if search:
            base_integrator_domain += [
                "|",
                ("name", "ilike", search),
                ("website_description", "ilike", search),
            ]

        # group by country
        country_domain = list(base_integrator_domain)
        countries = partner_obj.sudo().read_group(
            country_domain,
            ["id", "country_id"],
            groupby="country_id",
            orderby="country_id",
        )
        countries_partners = partner_obj.sudo().search_count(country_domain)

        # flag active country
        for country_dict in countries:
            country_dict["active"] = (
                country
                and country_dict["country_id"]
                and country_dict["country_id"][0] == country.id
            )
        countries.insert(
            0,
            {
                "country_id_count": countries_partners,
                "country_id": (0, _("All Countries")),
                "active": bool(country is None),
            },
        )

        if country:
            base_integrator_domain += [("country_id", "=", country.id)]
            url = "/integrators/country/" + slug(country)
        else:
            url = "/integrators"

        url_args = {}
        if search:
            url_args["search"] = search
        if country_all:
            url_args["country_all"] = True

        partner_count = partner_obj.sudo().search_count(base_integrator_domain)
        pager = request.website.pager(
            url=url,
            total=partner_count,
            page=page,
            step=self._references_per_page,
            scope=7,
            url_args=url_args,
        )

        # search integrators matching current search parameters
        integrator_ids = partner_obj.sudo().search(
            base_integrator_domain,
            order="grade_id ASC, implemented_count DESC,"
            "contributor_count DESC, member_count DESC,"
            "display_name ASC",
            offset=pager["offset"],
            limit=self._references_per_page,
        )
        integrators = integrator_ids.sudo()

        google_map_integrator_ids = ",".join(map(str, [i.id for i in integrators]))
        google_maps_api_key = (
            request.env["ir.config_parameter"].sudo().get_param("google_maps_api_key")
        )

        values = {
            "countries": countries,
            "current_country": country,
            "integrators": integrators,
            "google_map_integrator_ids": google_map_integrator_ids,
            "pager": pager,
            "searches": post,
            "search_path": "%s" % werkzeug.url_encode(post),
            "google_maps_api_key": google_maps_api_key,
        }

        return request.render(
            "website_oca_integrator.integrator_index",
            values,
            status=integrators and 200 or 404,
        )

    def get_integrator_modules_list(self, integrator):
        """
        Returns 5 favourite modules selected by integrator. If integrator has
        not selected 5 modules, then returns latest 5 developed modules.
        """
        module_display_count = 5
        favourite_modules = integrator.favourite_module_ids.filtered("is_published")
        developed_modules = integrator.developed_module_ids.filtered("is_published")
        favourite_module_count = len(favourite_modules)
        developed_module_count = len(developed_modules)

        remaining_modules = module_display_count - favourite_module_count

        # if integrator has developed less than 5 modules then
        # remaining modules are just other than favourite modules.
        if developed_module_count < module_display_count:
            remaining_modules = developed_module_count - favourite_module_count

        if remaining_modules:
            remaining_product_tmpl_ids = list(
                set(developed_modules.ids) - set(favourite_modules.ids)
            )
            # search latest product variant of module.
            sorted_modules = request.env["product.product"].search(
                [("product_tmpl_id", "in", remaining_product_tmpl_ids)],
                order="create_date desc",
            )

            sorted_modules = sorted_modules.mapped("product_tmpl_id")[
                :remaining_modules
            ]

            favourite_modules += sorted_modules

        return favourite_modules, developed_module_count

    def get_integrator_references(self, integrator):
        # sort integrator references by implemented date.
        references = integrator.implemented_partner_ids.sorted(
            key=lambda r: r.implemented_date or "", reverse=True
        )

        references = list(filter(lambda x: x.website_published is True, references))

        return references

    @http.route(
        ["/integrators/<integrator_id>"], type="http", auth="public", website=True
    )
    def integrators_detail(self, integrator_id, **post):
        """
        Display integrator's detail.
        """
        _, integrator_id = unslug(integrator_id)
        current_country = None
        country_id = post.get("country_id")

        if country_id:
            current_country = (
                request.env["res.country"].browse(int(country_id)).exists()
            )
        if integrator_id:
            integrator = request.env["res.partner"].sudo().browse(integrator_id)

            is_website_publisher = request.env["res.users"].has_group(
                "website.group_website_publisher"
            )

            if integrator.sudo().exists() and (
                integrator.website_published or is_website_publisher
            ):

                modules_list, developed_module_count = self.get_integrator_modules_list(
                    integrator
                )

                references = self.get_integrator_references(integrator)

                sponsorship_lines = integrator.sponsorship_line_ids.sorted(
                    key=lambda r: r.date_end, reverse=True
                )[:5]

                display_all_modules = True if developed_module_count > 5 else False

                values = {
                    "main_object": integrator,
                    "integrator": integrator,
                    "current_country": current_country,
                    "references": references,
                    "modules_list": modules_list,
                    "sponsorship_lines": sponsorship_lines,
                    "display_all_modules": display_all_modules,
                }
                return request.render("website_oca_integrator.integrators", values)
        return self.integrators(**post)

    @http.route(
        [
            "/integrators/<integrator_id>/contributors",
            "/integrators/<integrator_id>/contributors/page/<int:page>",
            "/integrators/<integrator_id>/contributors/country/<int:country_id>",
            "/integrators/<integrator_id>/contributors/country/"
            "<int:country_id>/page/<int:page>",
            "/integrators/<integrator_id>/contributors/country/"
            "<country_name>-<int:country_id>",
            "/integrators/<integrator_id>/contributors/country/"
            "<country_name>-<int:country_id>/page/<int:page>",
        ],
        type="http",
        auth="public",
        website=True,
    )
    def integrator_contributors(
        self, integrator_id=None, country_name=None, country_id=0, page=1, **post
    ):
        integrator = integrator_id
        integrator_name, integrator_id = unslug(integrator_id)
        country = request.env["res.country"]
        partner = request.env["res.partner"]

        post_name = post.get("search") or post.get("name", "")
        current_country = None

        country_domain = [
            "|",
            ("membership_state", "=", "paid"),
            ("github_login", "!=", False),
            ("website_published", "=", True),
            ("parent_id", "=", integrator_id),
        ]

        if post_name:
            country_domain += [
                "|",
                ("name", "ilike", post_name),
                ("website_description", "ilike", post_name),
            ]

        countries = partner.sudo().read_group(
            country_domain,
            ["id", "country_id"],
            groupby="country_id",
            orderby="country_id",
        )

        countries_total = sum(
            country_dict["country_id_count"] for country_dict in countries
        )

        if country_id:
            country_domain += [("country_id", "=", country_id)]
            current_country = country.browse(country_id).read(["id", "name"])[0]
            if not any(
                x["country_id"][0] == country_id for x in countries if x["country_id"]
            ):
                countries.append(
                    {
                        "country_id_count": 0,
                        "country_id": (country_id, current_country["name"]),
                    }
                )

                countries = [d for d in countries if d["country_id"]]
                countries.sort(key=lambda d: d["country_id"][1])

        countries.insert(
            0,
            {
                "country_id_count": countries_total,
                "country_id": (0, _("All Countries")),
            },
        )

        base_url = "/integrators/{}/contributors{}".format(
            integrator, "/country/%s" % country_id if country_id else "",
        )

        contributors_count = partner.sudo().search_count(country_domain)

        pager = request.website.pager(
            url=base_url,
            total=contributors_count,
            page=page,
            step=self._references_per_page,
            scope=7,
            url_args=post,
        )

        contributors = partner.sudo().search(
            country_domain,
            order="display_name ASC",
            offset=pager["offset"],
            limit=self._references_per_page,
        )

        values = {
            "contributors": contributors,
            "integrator": integrator,
            "countries": countries,
            "current_country": current_country
            and [current_country["id"], current_country["name"]]
            or None,
            "current_country_id": current_country and current_country["id"] or 0,
            "pager": pager,
            "post": post,
            "search": "?%s" % werkzeug.url_encode(post),
        }

        return request.render("website_oca_integrator.contributor_index", values)
