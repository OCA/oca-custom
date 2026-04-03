# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request, route

from odoo.addons.portal.controllers.portal import CustomerPortal


class IntegratorPortal(CustomerPortal):
    def _get_optional_fields(self):
        fields = list(super()._get_optional_fields())
        for f in [
            "favourite_module_ids",
            "github_organization",
        ]:
            if f not in fields:
                fields.append(f)
        return fields

    @route()
    def account(self, redirect=None, **post):
        if post:
            modules = request.httprequest.form.getlist("favourite_module_ids")
            if not modules:
                modules = post.get("favourite_module_ids")
                if modules:
                    modules = modules.split(",")
            if modules:
                post["favourite_module_ids"] = [int(id) for id in modules]
            else:
                post["favourite_module_ids"] = False
        return super().account(redirect=redirect, **post)

    @http.route(
        "/my/account/get_developed_modules",
        type="http",
        auth="user",
        methods=["GET"],
        website=True,
        sitemap=False,
    )
    def integrator_developed_module_read(self, query="", limit=25, **post):
        integrator = request.env.user.partner_id
        modules_data = request.env["product.template"].search_read(
            [
                ("id", "in", integrator.developed_module_ids.ids),
                ("name", "=ilike", "%" + (query or "") + "%"),
            ],
            fields=["id", "name"],
            limit=int(limit),
        )
        return request.make_json_response(modules_data)

    @http.route(
        "/my/account/get_favourite_modules",
        type="http",
        auth="user",
        methods=["GET"],
        website=True,
        sitemap=False,
    )
    def integrator_favourite_module_read(self):
        integrator = request.env.user.partner_id
        modules = integrator.favourite_module_ids
        modules_data = [{"id": m.id, "name": m.name} for m in modules]
        return request.make_json_response(modules_data)

    def details_form_validate(self, data):
        # after adding HTML editor in portal page, if we click on
        # 'Confirm' button then, 'files' key is passed in post data.
        # this field does not exist in 'res.partner'. removed this
        # key to prevent an error of "Unknown field 'files'".
        data.pop("files", False)
        error, error_message = super().details_form_validate(data)
        return error, error_message
