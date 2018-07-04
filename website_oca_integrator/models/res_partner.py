# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_integrator = fields.Boolean(string='Intergrator',
                                   compute='_compute_intergrator',
                                   store=True)

    contributor_count = fields.Integer(string='Number of contributors',
                                       compute='_compute_contributor_count',
                                       store=True)

    member_count = fields.Integer(string='Number of members',
                                  compute='_compute_member_count',
                                  store=True)

    module_count = fields.Integer(string='Number of modules',
                                  compute='_compute_module_count',
                                  store=True)

    @api.one
    @api.depends(
        'child_ids',
        'child_ids.membership_state',
        'child_ids.parent_id',
        'child_ids.website_published')
    def _compute_intergrator(self):
        if any([child.website_published and (
            child.github_login or child.membership_state == 'paid') for
                child in self.child_ids]):
            self.is_integrator = True
        else:
            self.is_integrator = False

    @api.one
    @api.depends('child_ids.github_login', 'child_ids.parent_id',
                 'child_ids.website_published')
    def _compute_contributor_count(self):
        self.contributor_count = len(self.child_ids.filtered(
            lambda
            child: child.github_login
            and child.website_published and child.membership_state != 'paid'))

    @api.one
    @api.depends('child_ids.membership_state', 'child_ids.parent_id',
                 'child_ids.website_published')
    def _compute_member_count(self):
        self.member_count = len(self.child_ids.filtered(
            lambda
            child: child.website_published
            and child.membership_state == 'paid'))

    @api.one
    @api.depends('author_ids', 'author_ids.partner_id')
    def _compute_module_count(self):
        self.module_count = sum(
            [author.module_qty for author in self.author_ids])
