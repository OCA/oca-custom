# Copyright 2026 Akretion (https://www.akretion.com).
# @author Benoit GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "OCA Membership Subscription",
    "summary": "Membership with subscription management",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "custom",
    "website": "https://github.com/OCA/oca-custom",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "membership_delegated_partner_line",
        "subscription_oca",
        "account_invoice_start_end_dates",
        "membership_variable_period",
    ],
    "data": [
        "views/sale_subscription.xml",
    ],
    "demo": [],
}
