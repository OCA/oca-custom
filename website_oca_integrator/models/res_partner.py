# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    github_organization = fields.Char()

    github_organization_url = fields.Char(
        string='Github Organization URL',
        compute='_compute_github_organization_url',
        store=True)

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

    implemented_date = fields.Date()

    author_ids = fields.One2many(comodel_name='odoo.author',
                                 string='Authors', inverse_name='partner_id',
                                 readonly=True)

    developed_module_ids = fields.Many2many(
        string='Developed Modules',
        comodel_name='product.template',
        relation='product_module_res_partner_rel',
        column1='partner_id',
        column2='product_template_id',
        compute='_compute_developed_modules',
        store=True)

    favourite_module_ids = fields.Many2many(
        string='Favourite Modules',
        comodel_name='product.template',
        relation='favourite_product_module_res_partner_rel',
        column1='partner_id',
        column2='product_template_id', readonly=True)

    sponsorship_line_ids = fields.One2many(
        string='Sponsorship Activities',
        comodel_name='sponsorship.line',
        inverse_name='partner_id')

    @api.multi
    @api.depends('github_organization')
    def _compute_github_organization_url(self):
        github_url = 'https://github.com/'
        for record in self:
            if record.is_company:
                github_organization = record.github_organization
                if github_organization:
                    record.github_organization_url = \
                        github_url + github_organization
                else:
                    record.github_organization_url = False

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
    @api.depends('author_ids', 'author_ids.partner_id',
                 'author_ids.module_qty')
    def _compute_module_count(self):
        for partner in self:
            partner.module_count = sum(
                [author.module_qty for author in partner.author_ids])

    @api.multi
    @api.depends('author_ids', 'is_integrator',
                 'author_ids.module_ids.product_template_id')
    def _compute_developed_modules(self):
        for partner in self:
            if partner.is_integrator:
                module_list = self.env['odoo.module'].search(
                    [('author_ids', 'in', partner.author_ids.ids)])
                product_list = self.env['product.template'].search(
                    [('odoo_module_id', 'in', module_list.ids)])
                partner.developed_module_ids = [(6, 0, product_list.ids)]

    @api.multi
    def write(self, vals):
        # clear github organization data if partner is not company
        if not vals.get('is_company', True):
            vals['github_organization'] = False
        res = super(ResPartner, self).write(vals)
        return res
