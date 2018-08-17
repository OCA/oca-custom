# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
import logging


from odoo import api, fields, models

_logger = logging.getLogger(__name__)


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

    contributor_module_line_ids = fields.One2many(
        string='Contributed Modules',
        comodel_name='contributor.module',
        inverse_name='partner_id', readonly=True)

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

    def update_contributor_modules(self, contributor, modules):
        """
        Update contributor with fetched modules from Github.
        """
        github_product_templates = self.env['odoo.module'].search(
            [('technical_name', 'in', list(modules.keys()))]).mapped(
            'product_template_id')

        contributor_module_lines = contributor.contributor_module_line_ids
        product_mapped_data = dict([(x.product_template_id.id, x.id) for x in
                                    contributor_module_lines])
        current_product_templates = contributor_module_lines.mapped(
            'product_template_id')

        total_product_templates = github_product_templates \
            | current_product_templates
        common_product_templates = github_product_templates \
            & current_product_templates
        new_product_templates = github_product_templates \
            - current_product_templates

        update_records = [(1, product_mapped_data[x.id], {
            'date_pr_merged': modules[x.odoo_module_id.technical_name]})
            for x in common_product_templates]
        new_records = [(0, 0,
                        {'product_template_id': x.id,
                         'date_pr_merged': modules[
                             x.odoo_module_id.technical_name]})
                       for x in new_product_templates]

        if len(total_product_templates) <= 5:
            contributor.write(
                {'contributor_module_line_ids': update_records + new_records})
        else:
            remove_products_count = len(total_product_templates) - 5
            delete_records = [(3, x.id, False) for x in
                              contributor_module_lines.sorted(
                                  key='date_pr_merged')[
                              :remove_products_count]]
            contributor.write(
                {'contributor_module_line_ids': update_records +
                 new_records + delete_records})

    def get_github_user_modules(self, user_data, github_connector,
                                all_modules_len):
        """
        Find latest 5 technical name of the modules based on the PR
        which are opened for OCA organization by github user.
        """
        current_page_modules = {}  # holds module name and merged date of PR.
        for x in user_data:
            org = x.get('org') and x['org']['login']
            if x['type'] == 'PullRequestEvent' and org == 'OCA' and \
                    x['payload']['action'] == 'opened':
                pull_request = x['payload']['pull_request']
                try:
                    pr_data = github_connector.get_by_url(
                        pull_request['url'], 'get')
                except Exception:
                    _logger.warning(
                        "Error while calling url '%s' while fetching"
                        "module for '%s'." %
                        (pull_request['url'], x['actor']['login']))
                    continue
                if pr_data['merged']:
                    commit_sha = pull_request['head']['sha']
                    # commit url of repo from which PR is created.
                    commit_url = pull_request['head']['repo']['commits_url']\
                        .replace('{/sha}', '/' + commit_sha)
                    try:
                        commit_data = github_connector.get_by_url(
                            commit_url, 'get')
                    except Exception:
                        _logger.warning(
                            "Error while calling url '%s' while "
                            "fetching module for '%s'." %
                            (pull_request['url'], x['actor']['login']))
                        continue

                    # find module name(s) from all committed files
                    for commit_file in commit_data['files']:
                        if len(current_page_modules) + all_modules_len >= 5:
                            return current_page_modules
                        file_name = commit_file.get(
                            'filename').split('/')[0].split('.')
                        # if length of filename is 1 then filename
                        # can be technical name of module
                        if len(file_name) == 1 and not \
                                file_name[0] in current_page_modules:
                            module_name = file_name
                            odoo_module = self.env['odoo.module'].search(
                                [('technical_name', 'in', module_name)])
                            if odoo_module:
                                date = datetime.datetime.strptime(
                                    pr_data['merged_at'],
                                    "%Y-%m-%dT%H:%M:%SZ").strftime(
                                    '%Y-%m-%d %H:%M:%S')
                                current_page_modules[module_name[0]] = date

        return current_page_modules

    def contributors_fetch_modules(self):
        all_modules = {}

        contributors = self.env['res.partner'].search(
            ['&', ('github_login', '!=', False),
             ('website_published', '=', True)])
        github_connector = self.env[
            'abstract.github.model'].get_github_connector('user')

        for record in contributors:
            contributor_login = record.github_login + '/events'
            # github API is limited to only 10 pages.
            for page in range(1, 11):
                try:
                    user_data = github_connector.get([contributor_login],
                                                     page=page)
                except Exception:
                    _logger.warning("Github login for partner '%s' is not"
                                    "correctly set." % (record.name))
                    break
                res = self.get_github_user_modules(
                    user_data, github_connector, len(all_modules))
                all_modules.update(res)
                if len(all_modules) == 5:
                    break
            self.update_contributor_modules(record, all_modules)

    def cron_create_github_user_module(self):
        self.contributors_fetch_modules()
