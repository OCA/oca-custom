# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "OCA Sponsors",
    "description": """Add and manage sponsors data for OCA website""",
    "version": "18.0.1.0.0",
    "author": "Akretion",
    "website": "https://github.com/oca/oca-custom",
    "license": "AGPL-3",
    "category": "Custom",
    "depends": [
        "membership_extension", # for security group
        "website_blog",
    ],
    "data": [
        # security
        "security/ir.model.access.csv",
        # data
        "data/mail_activity_data.xml",
        # views
        "views/blog_post.xml",
        "views/res_partner_industry.xml",
        "views/res_partner.xml",
        "views/sponsorship_line.xml",
    ],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
}
