# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "OCA Membership Groups (custom)",
    "version": "18.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/oca-custom",
    "license": "AGPL-3",
    "category": "Custom",
    "depends": [
        "mail_group",
        "oca_membership",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "views/mail_group.xml",
        "views/mail_group_member.xml",
        "views/membership_category.xml",
        "views/res_partner.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
}
