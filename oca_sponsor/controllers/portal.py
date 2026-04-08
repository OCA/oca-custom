# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

from ..models.res_partner import SPONSOR_WEBSITE_FIELDS


class CustomerPortalSponsor(CustomerPortal):
    def _prepare_portal_layout_values(self):
        return super()._prepare_portal_layout_values() | {
            "industries": request.env["res.partner.industry"].sudo().search([])
        }

    def details_form_validate(self, data, partner_creation=False):
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
