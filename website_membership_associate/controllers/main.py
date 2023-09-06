import werkzeug.urls

from odoo import fields, http
from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.website_membership.controllers.main import WebsiteMembership


class WebsiteMembership(WebsiteMembership):
    _references_per_page = 20

    @http.route(
        [
            "/members",
            "/members/page/<int:page>",
            "/members/association/<membership_id>",
            "/members/association/<membership_id>/page/<int:page>",
            "/members/country/<int:country_id>",
            "/members/country/<country_name>-<int:country_id>",
            "/members/country/<int:country_id>/page/<int:page>",
            "/members/country/<country_name>-<int:country_id>/page/<int:page>",
            "/members/association/<membership_id>/country/<country_name>-<int:country_id>",
            "/members/association/<membership_id>/country/<int:country_id>",
            "/members/association/<membership_id>/country/"
            "<country_name>-<int:country_id>/page/<int:page>",
            "/members/association/<membership_id>/country/<int:country_id>/page/<int:page>",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def members(
        self, membership_id=None, country_name=None, country_id=0, page=1, **post
    ):
        Product = request.env["product.product"]
        Country = request.env["res.country"]
        Partner = request.env["res.partner"]

        post_name = post.get("search") or post.get("name", "")
        current_country = None
        today = fields.Date.today()

        # base domain for groupby / searches
        base_line_domain = [
            ("website_published", "=", True),
            ("membership_state", "=", "paid"),
            ("membership_stop", ">=", today),
            ("membership_start", "<=", today),
        ]
        if membership_id and membership_id != "free":
            membership_id = int(membership_id)
            base_line_domain.append(("membership_id", "=", membership_id))

        if post_name:
            base_line_domain += [
                "|",
                ("name", "ilike", post_name),
                ("website_description", "ilike", post_name),
            ]

        # group by country, based on all customers (base domain)
        if membership_id != "free":
            membership_lines = Partner.sudo().search(base_line_domain)
            country_domain = [("id", "in", membership_lines.ids)]
            if not membership_id:
                country_domain = [
                    "|",
                    country_domain[0],
                    ("membership_state", "=", "free"),
                ]
        else:
            country_domain = [("membership_state", "=", "free")]

        countries = Partner.sudo().read_group(
            country_domain,
            ["id", "country_id"],
            groupby="country_id",
            orderby="country_id",
        )
        countries_total = sum(
            country_dict["country_id_count"] for country_dict in countries
        )

        line_domain = list(base_line_domain)
        if country_id:
            line_domain.append(("country_id", "=", country_id))
            current_country = Country.browse(country_id).read(["id", "name"])[0]
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

        # format domain for group_by and memberships
        memberships = Product.search(
            [("membership", "=", True)], order="website_sequence"
        )

        # make sure we don't access to lines with unpublished membershipts
        line_domain.append(("membership_id", "in", memberships.ids))

        limit = self._references_per_page
        offset = limit * (page - 1)

        count_members = 0
        membership_lines = Partner.sudo()
        # displayed non-free membership lines
        if membership_id != "free":
            count_members = Partner.sudo().search_count(line_domain)
            if offset <= count_members:
                membership_lines = Partner.sudo().search(line_domain, offset, limit)
        page_partner_ids = set(membership_lines.ids)

        # get google maps localization of partners
        google_map_partner_ids = []
        if request.website.is_view_active("website_membership.opt_index_google_map"):
            google_map_partner_ids = (
                Partner.sudo()
                .search(line_domain)
                .commercial_partner_id.filtered(
                    lambda s: s.is_published and s.is_company
                )[:2000]
            )

        search_domain = [
            ("membership_state", "=", "free"),
            ("website_published", "=", True),
        ]
        if post_name:
            search_domain += [
                "|",
                ("name", "ilike", post_name),
                ("website_description", "ilike", post_name),
            ]
        if country_id:
            search_domain += [("country_id", "=", country_id)]
        free_partners = Partner.sudo().search(search_domain)

        # Products
        memberships_data = []
        memberships_partner_ids = {}
        for membership_record in memberships:
            memberships_data.append(
                {"id": membership_record.id, "name": membership_record.name}
            )
            memberships_partner_ids[membership_record.id] = membership_lines.filtered(
                lambda s: s.membership_id.id == membership_record.id
            ).ids

        if free_partners:
            memberships_data.append({"id": "free", "name": _("Free Members")})
            if not membership_id or membership_id == "free":
                if count_members < offset + limit:
                    free_start = max(offset - count_members, 0)
                    free_end = max(offset + limit - count_members, 0)
                    memberships_partner_ids["free"] = free_partners.ids[
                        free_start:free_end
                    ]
                    page_partner_ids |= set(memberships_partner_ids["free"])
                google_map_partner_ids += free_partners.ids[
                    : 2000 - len(google_map_partner_ids)
                ]
                count_members += len(free_partners)

        google_map_partner_ids = ",".join(str(it) for it in google_map_partner_ids)
        google_maps_api_key = request.website.google_maps_api_key

        partners = {p.id: p for p in Partner.sudo().browse(list(page_partner_ids))}

        base_url = "/members%s%s" % (
            "/association/%s" % membership_id if membership_id else "",
            "/country/%s" % country_id if country_id else "",
        )

        # request pager for lines
        pager = request.website.pager(
            url=base_url,
            total=count_members,
            page=page,
            step=limit,
            scope=7,
            url_args=post,
        )

        values = {
            "partners": partners,
            "memberships_data": memberships_data,
            "memberships_partner_ids": memberships_partner_ids,
            "membership_id": membership_id,
            "countries": countries,
            "current_country": current_country
            and [current_country["id"], current_country["name"]]
            or None,
            "current_country_id": current_country and current_country["id"] or 0,
            "google_map_partner_ids": google_map_partner_ids,
            "pager": pager,
            "post": post,
            "search": "?%s" % werkzeug.urls.url_encode(post),
            "search_count": count_members,
            "google_maps_api_key": google_maps_api_key,
        }
        return request.render("website_membership.index", values)
