# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website OCA PSC Team',
    'summary': 'Displays PSC Teams in website.',
    'version': '11.0.1.0.0',
    'category': 'Website',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/oca-custom',
    'author': 'Odoo Community Association (OCA), Surekha Technologies',
    'depends': [
        'project',
        'github_connector',
        'project_members',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
    ],
    'demo': [
        'demo/project.xml',
    ],
    'installable': True,
}
