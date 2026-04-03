# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import Command, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from ..models.res_partner import SPONSOR_WEBSITE_FIELDS

AVATAR_MAX_SIZE = 2 * 1024 * 1024 # 2 Mo
AVATAR_ALLOWED_MIMETYPES = {
    "image/jpeg", "image/png",
}

class CustomerPortalSponsor(CustomerPortal):

    def _prepare_portal_layout_values(self):
        return super()._prepare_portal_layout_values() | {
            "industries": request.env["res.partner.industry"].sudo().search([])
        }

    def details_form_validate(self, data, partner_creation=False):
        error, error_message = super().details_form_validate(data, partner_creation)

        # many2many fields
        for field in ["sponsor_country_ids", "sponsor_industry_ids"]:
            if data.get(field):
                response = request.httprequest.form.getlist(field)
                data[field] = [Command.set([int(id) for id in response])]

        # avatar
        image_file = request.httprequest.files.get("image_1920")
        if image_file and image_file.filename:
            mimetype = image_file.mimetype or ""
            content = image_file.read()
            if mimetype not in AVATAR_ALLOWED_MIMETYPES:
                error["image_1920"] = _("Unauthorized format (JPG or PNG only).")
            elif len(content) > AVATAR_MAX_SIZE:
                error["image_1920"] = _("File is too big (%d Mo max).", AVATAR_MAX_SIZE / 1024 / 1024)
            else:
                data["image_1920"] = base64.b64encode(content)
            image_file.seek(0)

        return error, error_message

    def _get_optional_fields(self):
        optional = super()._get_optional_fields()
        mandatory = super()._get_mandatory_fields()
        return (
            optional +
            ["sponsor_country_ids", "sponsor_industry_ids"] +
            [
                f for f in SPONSOR_WEBSITE_FIELDS
                if f not in optional and f not in mandatory
            ]
        )
