# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    github_organization = fields.Char()

    github_organization_url = fields.Char(
        string="Github Organization URL",
        compute="_compute_github_organization_url",
        store=True,
    )

    is_integrator = fields.Boolean(
        string="Integrator", compute="_compute_integrator", store=True
    )

    contributor_count = fields.Integer(
        string="Number of contributors",
        compute="_compute_contributor_count",
        store=True,
    )

    member_count = fields.Integer(
        string="Number of members", compute="_compute_member_count", store=True
    )

    module_count = fields.Integer(
        string="Number of modules", compute="_compute_module_count", store=True
    )

    implemented_date = fields.Date()

    author_ids = fields.One2many(
        comodel_name="odoo.author",
        string="Authors",
        inverse_name="partner_id",
        readonly=True,
    )

    developed_module_ids = fields.Many2many(
        string="Developed Modules",
        comodel_name="product.template",
        relation="product_module_res_partner_rel",
        column1="partner_id",
        column2="product_template_id",
        compute="_compute_developed_modules",
        store=True,
    )

    favourite_module_ids = fields.Many2many(
        string="Favourite Modules",
        comodel_name="product.template",
        relation="favourite_product_module_res_partner_rel",
        column1="partner_id",
        column2="product_template_id",
        readonly=True,
    )

    sponsorship_line_ids = fields.One2many(
        string="Sponsorship Activities",
        comodel_name="sponsorship.line",
        inverse_name="partner_id",
    )

    contributor_module_line_ids = fields.One2many(
        string="Contributed Modules",
        comodel_name="contributor.module.line",
        inverse_name="partner_id",
        readonly=True,
    )

    @api.depends("github_organization")
    def _compute_github_organization_url(self):
        github_url = "https://github.com/"
        for record in self:
            if record.is_company:
                github_organization = record.github_organization
                if github_organization:
                    record.github_organization_url = github_url + github_organization
                else:
                    record.github_organization_url = False

    @api.depends("child_ids", "child_ids.membership_state", "child_ids.parent_id")
    def _compute_integrator(self):
        """
        Integrators are partners who have any contact with a commit
        to OCA repositories or a current OCA membership.
        """
        for partner in self:
            if any(
                [
                    (child.github_name or child.membership_state == "paid")
                    for child in partner.child_ids
                ]
            ):
                partner.is_integrator = True
            else:
                partner.is_integrator = False

    @api.depends("child_ids.github_name", "child_ids.parent_id")
    def _compute_contributor_count(self):
        contributor_data = self.read_group(
            domain=[("parent_id", "in", self.ids), ("github_name", "!=", False)],
            fields=["parent_id"],
            groupby=["parent_id"],
        )

        contributor_mapped_data = {
            item["parent_id"][0]: item["parent_id_count"] for item in contributor_data
        }

        for partner in self:
            partner.contributor_count = contributor_mapped_data.get(partner.id, 0)

    @api.depends("child_ids.membership_state", "child_ids.parent_id")
    def _compute_member_count(self):
        member_data = self.read_group(
            domain=[("parent_id", "in", self.ids), ("membership_state", "=", "paid")],
            fields=["parent_id"],
            groupby=["parent_id"],
        )

        member_mapped_data = {
            item["parent_id"][0]: item["parent_id_count"] for item in member_data
        }

        for partner in self:
            partner.member_count = member_mapped_data.get(partner.id, 0)

    @api.depends("author_ids", "author_ids.partner_id", "author_ids.module_qty")
    def _compute_module_count(self):
        for partner in self:
            partner.module_count = sum(
                [author.module_qty for author in partner.author_ids]
            )

    @api.depends(
        "author_ids", "is_integrator", "author_ids.module_ids.product_template_id"
    )
    def _compute_developed_modules(self):
        for partner in self:
            if partner.is_integrator:
                module_list = self.env["odoo.module"].search(
                    [("author_ids", "in", partner.author_ids.ids)]
                )
                product_list = self.env["product.template"].search(
                    [("odoo_module_id", "in", module_list.ids)]
                )
                partner.developed_module_ids = [(6, 0, product_list.ids)]

    def write(self, vals):
        # clear github organization data if partner is not company
        if not vals.get("is_company", True):
            vals["github_organization"] = False
        res = super().write(vals)
        return res

    def update_contributor_modules(self, contributor, modules):
        """
        Update contributor with fetched modules from Github.
        """
        github_templates = (
            self.env["odoo.module"]
            .search([("technical_name", "in", list(modules.keys()))])
            .mapped("product_template_id")
        )

        contributor_module_lines = contributor.contributor_module_line_ids
        product_mapped_data = {
            line.product_template_id.id: line.id for line in contributor_module_lines
        }
        current_templates = contributor_module_lines.mapped("product_template_id")

        total_templates = github_templates | current_templates
        common_templates = github_templates & current_templates
        new_templates = github_templates - current_templates

        update_records = [
            (
                1,
                product_mapped_data[product.id],
                {"date_pr_merged": modules[product.odoo_module_id.technical_name]},
            )
            for product in common_templates
        ]
        new_records = [
            (
                0,
                0,
                {
                    "product_template_id": product.id,
                    "date_pr_merged": modules[product.odoo_module_id.technical_name],
                },
            )
            for product in new_templates
        ]
        delete_records = []

        if len(total_templates) > 5:
            remove_products_count = len(total_templates) - 5
            delete_records = [
                (2, line.id, False)
                for line in contributor_module_lines.sorted(key="date_pr_merged")[
                    :remove_products_count
                ]
            ]

        contributor.write(
            {
                "contributor_module_line_ids": update_records
                + new_records
                + delete_records
            }
        )

    def get_github_user_modules(self, gh_events, github_orgs):
        """
        Find latest 5 technical name of the modules based on the PR
        which are opened for OCA organization by github user.
        """
        current_page_modules = {}  # holds module name and merged date of PR.
        for gh_event in gh_events:
            org = gh_event.org and gh_event.org.login
            if (
                gh_event.type == "PullRequestEvent"
                and org in github_orgs
                and gh_event.payload["action"] == "opened"
            ):
                pr_number = gh_event.payload["pull_request"]["number"]
                try:
                    gh_pull_request = gh_event.repo.get_pull(pr_number)
                except Exception:
                    _logger.warning(
                        "Error while fetching pull request #'%s' of repository '%s'/'%s'."
                        % (pr_number, org, gh_event.repo)
                    )
                    continue
                if gh_pull_request.merged:
                    commit_sha = gh_pull_request.head.sha
                    gh_commit = gh_event.repo.get_commit(commit_sha)

                    for commit_file in gh_commit.files:
                        file_name = commit_file.filename.split("/")[0].split(".")
                        # if length of filename is 1 then filename
                        # can be technical name of module
                        if (
                            len(file_name) == 1
                            and not file_name[0] in current_page_modules
                        ):
                            module_name = file_name
                            odoo_module = self.env["odoo.module"].search(
                                [("technical_name", "in", module_name)]
                            )
                            if odoo_module:
                                date = gh_pull_request.merged_at
                                current_page_modules[module_name[0]] = date
                                if len(current_page_modules) == 5:
                                    return current_page_modules
        return current_page_modules

    def get_github_organization(self):
        return self.env["github.organization"].search([]).mapped("github_name")

    def get_contributors(self):
        contributors = self.env["res.partner"].search(
            ["&", ("github_name", "!=", False), ("website_published", "=", True)]
        )
        return contributors

    def contributors_fetch_modules(self):
        gh_api = self.get_github_connector()
        contributors = self.get_contributors()
        github_orgs = self.get_github_organization()

        for contributor in contributors:
            try:
                gh_user = gh_api.get_user(contributor.github_name)
            except Exception:
                _logger.warning("Error while fetching user '%s'." % (contributor.name))
                continue
            gh_events = gh_user.get_events()
            modules = self.get_github_user_modules(gh_events, github_orgs)
            self.update_contributor_modules(contributor, modules)

    def cron_create_github_user_module(self):
        self.contributors_fetch_modules()
