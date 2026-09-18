# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "OCA Membership (custom)",
    "version": "18.0.1.0.11",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/oca-custom",
    "license": "AGPL-3",
    "category": "Custom",
    "depends": [
        "account",
        "membership_extension",  # for membership.category
        "oca_vcp",
        "membership_account_invoice_start_end_dates",  # for invoice report
        "membership_delegated_partner_line",  # for invoice report
    ],
    "data": [
        "data/membership_category_data.xml",
        "data/res_groups.xml",
        "reports/report_invoice.xml",
        "views/membership_category.xml",
        "views/portal_templates.xml",
        "views/res_partner.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
}
