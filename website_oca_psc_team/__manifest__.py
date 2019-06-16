# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website OCA PSC Team',
    'summary': 'Displays PSC Teams in website.',
    'version': '12.0.1.0.0',
    'category': 'Website',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/oca-custom',
    'author': 'Odoo Community Association (OCA), Surekha Technologies',
    'depends': [
        'oca_psc_team',
        'website',
        'website_crm_partner_assign'
    ],
    'data': [
        'templates/assets.xml',
        'templates/psc_category_template.xml',
        'templates/website_oca_psc_team_data.xml',
    ],
    'demo': [
        'demo/res_users.xml',
    ],
    'installable': True,
    'auto_install': True,
}
