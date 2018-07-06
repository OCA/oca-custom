# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_integrator = fields.Boolean(string='Integrator',
                                   compute='_compute_integrator',
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

    @api.depends(
        'child_ids',
        'child_ids.membership_state',
        'child_ids.parent_id')
    def _compute_integrator(self):
        for partner in self:
            if any([(child.github_login or child.membership_state == 'paid')
                    for child in partner.child_ids]):
                partner.is_integrator = True
            else:
                partner.is_integrator = False

    @api.depends('child_ids.github_login', 'child_ids.parent_id')
    def _compute_contributor_count(self):
        contributor_data = self.read_group(
            domain=[('parent_id', 'in', self.ids),
                    ('github_login', '!=', False)], fields=['parent_id'],
            groupby=['parent_id'])

        contributor_mapped_data = dict(
            (item['parent_id'][0], item['parent_id_count']) for item in
            contributor_data)

        for partner in self:
            partner.contributor_count = contributor_mapped_data.get(
                partner.id, 0)

    @api.depends('child_ids.membership_state', 'child_ids.parent_id')
    def _compute_member_count(self):
        member_data = self.read_group(
            domain=[('parent_id', 'in', self.ids),
                    ('membership_state', '=', 'paid')], fields=['parent_id'],
            groupby=['parent_id'])

        member_mapped_data = dict(
            (item['parent_id'][0],
             item['parent_id_count']) for item in member_data)

        for partner in self:
            partner.member_count = member_mapped_data.get(partner.id, 0)

    @api.multi
    @api.depends('author_ids', 'author_ids.partner_id')
    def _compute_module_count(self):
        for partner in self:
            partner.module_count = sum(
                [author.module_qty for author in partner.author_ids])
