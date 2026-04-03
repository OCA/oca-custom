# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortalPublish(CustomerPortal):

    def _get_is_published_fields(self):
        return [
            "is_published",
            "is_published_email",
            "is_published_phone",
            "is_published_address",
            "is_published_website",
        ]

    def details_form_validate(self, data, partner_creation=False):
        # Published fields
        for field in self._get_is_published_fields():
            data[field] = field in data and bool(int(data[field]))
        return super().details_form_validate(data)

    def _get_optional_fields(self):
        return (
            super()._get_optional_fields() 
            + ["website"] + self._get_is_published_fields()
        )
