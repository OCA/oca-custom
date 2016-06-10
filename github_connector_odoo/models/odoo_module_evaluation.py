# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class OdooModuleEvaluation(models.Model):
    _name = 'odoo.module.evaluation'

    # Constant Section
    _RATING_SELECTION = [
        ('1', '1 - Description to define'),
        ('2', '2 - Description to define'),
        ('3', '3 - Description to define'),
        ('4', '4 - Description to define'),
        ('5', '5 - Description to define'),
    ]

    summary = fields.Char(
        string='Appreciation Summary')

    comment = fields.Text(string='Detailled Appreciation')

    rating = fields.Selection(
        string='Appreciation', selection=_RATING_SELECTION, required=True)

    module_id = fields.Many2one(
        string='Module', comodel_name='odoo.module', required=True)

    user_id = fields.Many2one(
        string='Author User', comodel_name='res.users', required=True,
        readonly=True, default=lambda self: self.env.user)

    partner_id = fields.Many2one(
        string='Author Partner', comodel_name='res.partner',
        related='user_id.partner_id', store=True, readonly=True)

    _sql_constraints = [
        ('module_user_uniq', 'unique (module_id, user_id)',
            "You can only vote one time for a module !"),
    ]
