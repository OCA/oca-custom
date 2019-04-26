# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ContributorModuleLine(models.Model):
    _name = 'contributor.module.line'
    _description = 'Contributor Line'

    product_template_id = fields.Many2one(
        string='Odoo Module',
        comodel_name='product.template',
        required=True
    )

    partner_id = fields.Many2one(comodel_name='res.partner', string="Partner",
                                 required=True)

    date_pr_merged = fields.Datetime(string="Merged date of PR", required=True)
