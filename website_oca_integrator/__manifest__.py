# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website OCA Integrator",
    "summary": "Displays Integrators in website.",
    "version": "18.0.1.0.2",
    "category": "Website",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/oca-custom",
    "author": "Odoo Community Association (OCA), Surekha Technologies",
    "depends": [
        "base",
        "website",
        "web_tour",
        "website_crm_partner_assign",
        "website_sale",
        "membership",
        "website_membership",
        "website_customer",
        "github_connector",
        "github_connector_odoo",
        "apps_product_creator",
        "oca_sponsor",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/website_oca_integrator_templates.xml",
        "views/website_oca_integrator_contributor_templates.xml",
        "views/view_portal_templates.xml",
        "views/website_oca_integrator_data.xml",
        "views/view_res_partner.xml",
        "views/view_odoo_author.xml",
        "data/ir_cron.xml",
    ],
    "external_dependencies": {"python": ["responses"]},
    "assets": {
        "web.assets_frontend": [
            "website_oca_integrator/static/src/js/integrator_portal.js",
            "website_oca_integrator/static/src/scss/website_oca_integrator.scss",
        ],
        "web.assets_tests": [
            "website_oca_integrator/static/src/js/integrator_portal_tour.js",
        ],
    },
    "installable": True,
    "development_status": "Alpha",
}
