# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "OCA Membership (custom)",
    "description": """Adapt membership processes for OCA needs""",
    "version": "18.0.1.0.0",
    "author": "Akretion",
    "website": "https://github.com/oca/oca-custom",
    "license": "AGPL-3",
    "category": "Custom",
    "depends": [
        "mail_group", # for Work Groups
        "membership_extension", # for membership.category
    ],
    "data": [
        "data/membership_category_data.xml",
        "views/mail_group.xml",
        "views/membership_category.xml",
        "views/res_partner.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
}
