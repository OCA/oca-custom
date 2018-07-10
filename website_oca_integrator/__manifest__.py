# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website OCA Integrator',
    'summary': 'Displays Integrators in website.',
    'version': "11.0.1.0.0",
    'category': 'Website',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/oca-custom',
    'author': 'Odoo Community Association (OCA), Surekha Technologies',
    'depends': [
        'base',
        'website',
        'website_crm_partner_assign',
        'membership',
        'github_connector_odoo',
    ],
    'data': [
        'views/website_oca_integrator_templates.xml',
        'views/website_oca_integrator_data.xml',
        'views/view_res_partner.xml',
        'views/view_odoo_author.xml',
    ],
    'installable': True,
}
