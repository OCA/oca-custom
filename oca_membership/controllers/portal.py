# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import _
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

AVATAR_MAX_SIZE = 2 * 1024 * 1024  # 2 Mo
AVATAR_ALLOWED_MIMETYPES = {
    "image/jpeg",
    "image/png",
}


class CustomerPortalPublish(CustomerPortal):
    def _get_boolean_fields(self):
        return [
            "is_published",
            "is_published_email",
            "is_published_phone",
            "is_published_address",
            "is_published_website",
            "github_sync_avatar",
        ]

    def details_form_validate(self, data, partner_creation=False):
        error, error_message = super().details_form_validate(data, partner_creation)

        # Published fields
        for field in self._get_boolean_fields():
            data[field] = field in data and data[field] in ("1", "on")

        # Avatar
        avatar_update = False
        image_file = request.httprequest.files.get("image_1920")
        if image_file and image_file.filename:
            mimetype = image_file.mimetype or ""
            content = image_file.read()
            if mimetype not in AVATAR_ALLOWED_MIMETYPES:
                error["image_1920"] = _("Unauthorized format (JPG or PNG only).")
            elif len(content) > AVATAR_MAX_SIZE:
                error["image_1920"] = _(
                    "File is too big (%d Mo max).", AVATAR_MAX_SIZE / 1024 / 1024
                )
            elif content:
                data["image_1920"] = base64.b64encode(content)
                avatar_update = True
            image_file.seek(0)
        if not avatar_update:
            data.pop("image_1920", None)

        return error, error_message

    def _get_optional_fields(self):
        return (
            ["website", "github_main_login"]
            + super()._get_optional_fields()
            + self._get_boolean_fields()
        )
