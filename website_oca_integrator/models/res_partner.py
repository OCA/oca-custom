# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import logging

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

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

    @api.multi
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
                    (child.github_login or child.membership_state == "paid")
                    for child in partner.child_ids
                ]
            ):
                partner.is_integrator = True
            else:
                partner.is_integrator = False

    @api.depends("child_ids.github_login", "child_ids.parent_id")
    def _compute_contributor_count(self):
        contributor_data = self.read_group(
            domain=[("parent_id", "in", self.ids), ("github_login", "!=", False)],
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

    @api.multi
    @api.depends("author_ids", "author_ids.partner_id", "author_ids.module_qty")
    def _compute_module_count(self):
        for partner in self:
            partner.module_count = sum(
                [author.module_qty for author in partner.author_ids]
            )

    @api.multi
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

    @api.multi
    def write(self, vals):
        # clear github organization data if partner is not company
        if not vals.get("is_company", True):
            vals["github_organization"] = False
        res = super(ResPartner, self).write(vals)
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

    def get_github_user_modules(
        self, event_response, github_connector, all_modules_len, github_orgs
    ):
        """
        Find latest 5 technical name of the modules based on the PR
        which are opened for OCA organization by github user.
        """
        current_page_modules = {}  # holds module name and merged date of PR.
        for event in event_response:
            org = event.get("org") and event["org"]["login"]
            if (
                event["type"] == "PullRequestEvent"
                and org in github_orgs
                and event["payload"]["action"] == "opened"
            ):
                pull_request = event["payload"]["pull_request"]
                try:
                    pr_response = self.get_github_api_response(
                        github_connector, pull_request["url"]
                    )
                except Exception:
                    _logger.warning(
                        "Error while calling url '%s' during fetching "
                        "module for '%s'."
                        % (pull_request["url"], event["actor"]["login"])
                    )
                    continue
                if pr_response["merged"]:
                    commit_sha = pull_request["head"]["sha"]
                    # commit url of repo from which PR is created.
                    commit_url = pull_request["head"]["repo"]["commits_url"].replace(
                        "{/sha}", "/" + commit_sha
                    )
                    try:
                        commit_data = self.get_github_api_response(
                            github_connector, commit_url
                        )
                    except Exception:
                        _logger.warning(
                            "Error while calling url '%s' during fetching "
                            "module for '%s'." % (commit_url, event["actor"]["login"])
                        )
                        continue

                    # find module name(s) from all committed files
                    for commit_file in commit_data["files"]:
                        if len(current_page_modules) + all_modules_len == 5:
                            return current_page_modules
                        file_name = commit_file.get("filename").split("/")[0].split(".")
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
                                date = datetime.datetime.strptime(
                                    pr_response["merged_at"], "%Y-%m-%dT%H:%M:%SZ"
                                ).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                current_page_modules[module_name[0]] = date

        return current_page_modules

    def get_github_api_response(self, github_connector, query_url):
        return github_connector.get_by_url(query_url, "get")

    def get_github_organization(self):
        return self.env["github.organization"].search([]).mapped("github_login")

    def get_contributors(self):
        contributors = self.env["res.partner"].search(
            ["&", ("github_login", "!=", False), ("website_published", "=", True)]
        )
        return contributors

    def contributors_fetch_modules(self):
        all_modules = {}
        github_users_api = "https://api.github.com/users/"
        event_url = "/events?page=%d"

        github_connector = self.env["abstract.github.model"].get_github_connector(
            "user"
        )
        contributors = self.get_contributors()
        github_orgs = self.get_github_organization()

        for contributor in contributors:
            contributor_event_url = (
                github_users_api + contributor.github_login + event_url
            )
            # github API is limited to only 10 pages.
            for page in range(1, 11):
                try:
                    event_response = self.get_github_api_response(
                        github_connector, contributor_event_url % (page)
                    )
                    if not event_response:
                        # if we get empty response in page then all
                        # other next pages will have empty response.
                        break
                except Exception:
                    _logger.warning(
                        "Github login for partner '%s' is not"
                        " correctly set." % (contributor.name)
                    )
                    break
                current_page_modules = self.get_github_user_modules(
                    event_response, github_connector, len(all_modules), github_orgs
                )
                all_modules.update(current_page_modules)
                if len(all_modules) == 5:
                    break
            self.update_contributor_modules(contributor, all_modules)
            all_modules.clear()

    def cron_create_github_user_module(self):
        self.contributors_fetch_modules()
