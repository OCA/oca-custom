# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Oca VCP",
    "summary": "OCA VCP customisation",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Custom",
    "website": "https://github.com/OCA/oca-custom",
    "author": " Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": ["pypandoc"],
        "bin": [],
    },
    "depends": [
        "vcp_odoo",
        "vcp_github",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/vcp_odoo_module_view.xml",
        "views/vcp_repository_view.xml",
        "views/vcp_repository_category_view.xml",
        "views/res_partner_view.xml",
    ],
    "demo": [],
}
