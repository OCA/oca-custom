# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "OCA monetization",
    "summary": "Nag users of OCA modules to buy a subscription",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/oca-customize",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "preloadable": True,
    "depends": [
        "web",
        "base_setup",
    ],
    "data": [
        "views/res_config_settings.xml",
        "views/templates.xml",
    ],
    "qweb": [
        "static/src/xml/oca_monetize.xml",
    ],
}
