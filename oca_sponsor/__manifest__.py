# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "OCA Sponsors",
    "version": "18.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/oca-custom",
    "license": "AGPL-3",
    "category": "Custom",
    "depends": [
        "html_editor",
        "mail_activity_team",
        "membership_extension",
        "website_blog",
        # Custom
        "oca_membership",
    ],
    "data": [
        "data/mail_activity_team.xml",
        "security/ir.model.access.csv",
        "views/blog_post.xml",
        "views/mail_activity.xml",
        "views/portal_templates.xml",
        "views/res_partner_industry.xml",
        "views/res_partner.xml",
        "views/sponsorship_line.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "oca_sponsor/static/src/**/*",
        ]
    },
    "installable": True,
    "application": False,
    "development_status": "Alpha",
}
