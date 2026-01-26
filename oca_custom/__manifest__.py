# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "OCA Custom Settings",
    "summary": "Custom Settings for OCA Instance",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "website": "https://github.com/OCA/oca-custom",
    "author": "GRAP, Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "base",
        "contacts",
        "github_connector",
        "membership",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "data/ir_action_server_data.xml",
        "views/res_config_settings.xml",
        "views/res_partner.xml",
    ],
    "installable": True,
}
