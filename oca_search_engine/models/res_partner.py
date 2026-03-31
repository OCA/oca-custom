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
    can_be_published = fields.Boolean(
        compute="_compute_can_be_published",
        search="_search_can_be_published",
    )
    
    #====== Search engine sync logics ======#
    def _add_to_oca_search_engine(self, vals={}):
        """Add, update or remove partners in index (persons & companies)"""
        def _add_or_remove(mode, partners):
            method = "_add_to_index" if mode == "add" else "_remove_from_index"
            companies = partners.filtered("is_company")
            individuals = partners - companies
            getattr(companies, method)(self.env.ref(INDEX_COMPANIES))
            getattr(individuals, method)(self.env.ref(INDEX_PERSONS))

        self._autopublish_companies(vals)
        to_synch = self.filtered(lambda x: x._filter_add_to_oca_search_engine())
        _add_or_remove("add", to_synch)
        _add_or_remove("remove", self - to_synch)
    
    def _filter_add_to_oca_search_engine(self):
        """`is_published` is a manual field in Odoo to start or stop the partner sync"""
        return self.can_be_published and self.is_published
    
    def _autopublish_companies(self, vals):
        """Auto-publish new integrators and new sponsors
        (but not members: because of individual acceptance),
        and remove partner manually set to "unpublished"
        """
        # if called from write: prevent re-publishing a company already unpublished
        if vals and not any(x in vals and vals[x] for x in ["grade_id", "is_integrator"]):
            return

        self.filtered(
            lambda x: x.is_company and x.can_be_published and not x.is_published
        ).sudo().is_published = True
        # 'sudo' to bypass AccessError of 'website.published.multi.mixin'

    #====== Compute ======#
    @api.depends("is_integrator", "grade_id", "membership_state")
    def _compute_can_be_published(self):
        """Technical field enabling or not `is_published`, this last being editable by internal users"""
        for partner in self:
            partner.can_be_published = partner._get_can_be_published()
    
    def _get_can_be_published(self):
        """`sponsor_to_review` is prioritary to prevent unreviewed data on the website"""
        return (
            (not self.is_sponsor or not self.sponsor_to_review) and (
                self.is_integrator or
                self.is_sponsor or
                self.membership_state in ["free", "paid"]
            )
        )
    
    @api.model
    def _search_can_be_published(self, operator, value):
        if operator != "=" or not isinstance(value, bool) or not value:
            raise NotImplementedError("Operation not supported.")
        return [
            "|", ("is_sponsor", "=", False), ("sponsor_to_review", "=", False),
            "|", "|",
                ("is_integrator", "=", True),
                ("is_sponsor", "=", True),
                ("membership_state", "in", ["free", "paid"]),
        ]
    
    #====== CRUD ======#
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._add_to_oca_search_engine()
        return records
    
    def copy(self, default={}):
        records = super().copy(default)
        records._add_to_oca_search_engine()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._add_to_oca_search_engine(vals)
        return res

    #===== Business logics =====#
    def _get_avatar_url(self, size):
        self.ensure_one()
        return f'{self.get_base_url()}/web/image/res.partner/{self.id}/avatar_{size}'
