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
        "mail_activity_team", # for sponsor review process
        "membership_extension", # for security groups
        "website_blog",
    ],
    "data": [
        "data/mail_activity_team.xml",
        "security/ir.model.access.csv",
        "views/blog_post.xml",
        "views/mail_activity.xml",
        "views/res_partner_industry.xml",
        "views/res_partner.xml",
        "views/sponsorship_line.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'oca_sponsor/static/src/**/*',
        ]
    },
    "installable": True,
    "application": False,
    "development_status": "Alpha",
}
