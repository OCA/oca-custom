# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

from ..models.res_partner import SPONSOR_WEBSITE_FIELDS


class CustomerPortalSponsor(CustomerPortal):
    def _prepare_portal_layout_values(self):
        res = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        if partner.grade_id.show_industry:
            res["industries"] = request.env["res.partner.industry"].sudo().search([])
        return res

    def details_form_validate(self, data, partner_creation=False):
        # industries are only allowed for some sponsor levels
        partner = request.env.user.partner_id
        if not partner.grade_id.show_industry:
            data["sponsor_industry_ids"] = False

        # many2many fields
        for field in ["sponsor_country_ids", "sponsor_industry_ids"]:
            if data.get(field):
                response = request.httprequest.form.getlist(field)
                data[field] = [Command.set([int(id) for id in response])]

        return super().details_form_validate(data)

    def _get_optional_fields(self):
        optional = super()._get_optional_fields()
        mandatory = super()._get_mandatory_fields()
        return (
            optional
            + ["sponsor_country_ids", "sponsor_industry_ids"]
            + [
                f
                for f in SPONSOR_WEBSITE_FIELDS
                if f not in optional and f not in mandatory
            ]
        )
