# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class GithubOrganizationSerie(models.Model):
    _name = 'github.organization.serie'
    _order = 'name'

    # Columns Section
    name = fields.Char(string='Name', required=True)

    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization')

    complete_name = fields.Char(
        string='Complete Name', store=True, compute='_compute_complete_name')

    # Compute Section
    @api.multi
    @api.depends('name', 'organization_id.name')
    def _compute_complete_name(self):
        for serie in self:
            serie.complete_name =\
                serie.organization_id.name + '/' + serie.name
