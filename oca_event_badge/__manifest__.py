# Copyright 2018 ACSONE SA/NV
# Copyright 2018 Tecnativa - Cristina Martin R.
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "OCA Event Badge",
    "summary": """
        Creates Custom Event Badges based on the Partner Tags""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/oca-custom",
    "category": "Custom",
    "depends": ["base", "event", "web"],
    "data": [
        "views/event_event_template_asset_report.xml",
        "views/event_event_templates.xml",
    ],
    "installable": True,
}
