# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "OCA PSC Team",
    "summary": "This module allows you to store PSC details in project."
    "These details will be displayed in PSC Teams in website.",
    "version": "14.0.1.0.0",
    "category": "Website",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/oca-custom",
    "author": "Odoo Community Association (OCA), Surekha Technologies",
    "depends": ["project", "github_connector", "project_members"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_views.xml",
        "views/psc_category_views.xml",
    ],
    "demo": [
        "demo/github_repository.xml",
        "demo/project.xml",
        "demo/psc_category.xml",
    ],
    "installable": True,
}
