# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.portal.controllers.portal import CustomerPortal


class IntegratorPortal(CustomerPortal):
    def details_form_validate(self, data):
        # after adding HTML editor in portal page, if we click on
        # 'Confirm' button then, 'files' key is passed in post data.
        # this field does not exist in 'res.partner'. removed this
        # key to prevent an error of "Unknown field 'files'".
        data.pop("files", False)
        error, error_message = super().details_form_validate(data)
        return error, error_message
