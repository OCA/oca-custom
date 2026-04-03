# Copyright 2026 Akretion (https://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

INDEX_COMPANIES = "oca_search_engine.oca_typesense_index_companies"
INDEX_PERSONS = "oca_search_engine.oca_typesense_index_persons"

class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "se.indexable.record", "abstract.url"]

    is_published = fields.Boolean(
        tracking=True,
        help="Whether this contact publicly appears on the website.\n"
             "Automatically enabled for companies (sponsors and integrators).\n"
             "To enable manually for individuals (members).",
    )
    is_published_email = fields.Boolean(string="Publish email", default=True)
    is_published_phone = fields.Boolean(string="Publish phone", default=True)
    is_published_address = fields.Boolean(string="Publish address", default=True)
    is_published_website = fields.Boolean(string="Publish website", default=True)

    #====== Search engine sync logics ======#
    def _add_to_oca_search_engine(self, vals={}):
        """Add, update or remove partners in 'Company' or 'Person' index"""
        companies = self.filtered("is_company")
        persons = self - companies

        if vals and "is_published" in vals and not vals["is_published"]:
            companies._remove_from_index(self.env.ref(INDEX_COMPANIES))
            persons._remove_from_index(self.env.ref(INDEX_PERSONS))
        else:
            companies._autopublish_companies(vals)
            companies._add_to_index(self.env.ref(INDEX_COMPANIES))
            persons._add_to_index(self.env.ref(INDEX_PERSONS))

    def _autopublish_companies(self, vals):
        """Auto-publish new integrators and new sponsors
        (but not members: because of individual acceptance),
        and remove partner manually set to "unpublished"
        """
        # if called from write: prevent re-publishing a company already unpublished
        if vals and not any(x in vals and vals[x] for x in ["grade_id", "is_integrator"]):
            return

        self.filtered(
            lambda x: x.is_company and not x.is_published
        ).sudo().is_published = True
        # 'sudo' to bypass AccessError of 'website.published.multi.mixin'

    #====== CRUD ======#
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._add_to_oca_search_engine()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._add_to_oca_search_engine(vals)
        return res
