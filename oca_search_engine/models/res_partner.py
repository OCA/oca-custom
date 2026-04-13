# Copyright 2026 Akretion (https://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

INDEX_COMPANIES = "oca_search_engine.oca_typesense_index_companies"
INDEX_PERSONS = "oca_search_engine.oca_typesense_index_persons"


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "se.indexable.record", "abstract.url"]

    # ====== Search engine sync logics ======#
    def _add_to_oca_search_engine(self, vals=None):
        """Add, update or remove partners in 'Company' or 'Person' index"""
        index_companies = self.env.ref(INDEX_COMPANIES)
        index_persons = self.env.ref(INDEX_PERSONS)

        if vals and "is_published" in vals and not vals["is_published"]:
            self._remove_from_index(index_companies | index_persons)
        else:
            self._autopublish_companies(vals)

            to_publish = self.filtered("is_published")
            companies = to_publish.filtered("is_company")
            persons = to_publish - companies
            companies._add_to_index(index_companies)
            persons._add_to_index(index_persons)

    def _autopublish_companies(self, vals):
        """Auto-publish new integrators and new sponsors
        (but not members: because of individual acceptance),
        and remove partner manually set to "unpublished"
        """
        # if called from write: prevent re-publishing a company already unpublished
        if vals and not any(
            x in vals and vals[x] for x in ["is_integrator", "grade_id"]
        ):
            return

        self.filtered(
            lambda x: not x.is_published and (x.is_integrator or x.is_sponsor)
        ).sudo().is_published = True
        # 'sudo' to bypass AccessError of 'website.published.multi.mixin'

    # ====== CRUD ======#
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._add_to_oca_search_engine()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._add_to_oca_search_engine(vals)
        return res

    # ===== Business logics =====#
    def _get_working_groups(self):
        return self.mail_group_member_ids.mail_group_id.filtered("is_working_group")

    def _get_company_members(self):
        return self.filtered("is_company").child_ids.filtered("is_member")
