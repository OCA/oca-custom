# Copyright 2026 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale OCA App Products Redirect",
    "summary": "Redirect all archived OCA-App-Related Products to the new shop",
    "version": "18.0.1.0.5",
    "category": "Website",
    "website": "https://github.com/OCA/oca-custom",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["website_sale", "website_partner"],
    "data": [
        "data/ir_config_parameter.xml",
        "security/ir_rule.xml",
        "views/templates.xml",
    ],
}
