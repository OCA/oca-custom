# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class OdooAuthor(models.Model):
    _inherit = 'odoo.author'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Company',
        domain="[('is_company','=', True),('website_published', '=', True)]",
        help="Select company which is linked to this Author.")
