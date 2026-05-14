# Copyright 2026 Akretion (https://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

INDEX_COMPANIES = "oca_search_engine.oca_typesense_index_companies"
INDEX_PERSONS = "oca_search_engine.oca_typesense_index_persons"


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "se.indexable.record", "abstract.url"]

    def _get_keyword_fields(self):
        # The _get_keyword field is call in base_url in two case
        # Called with a class in the @api.depends in order to flag
        # the url as invalid "url_need_refresh"
        # And on the record when recomputing the index
        # In our case we want to use the sponsor_name as keyword for the url key
        # if it's a company and the sponsor_name is filled
        # if not we use the name
        if not self:
            # It's the case of the @api.depends, both field will invalid
            # the "url_need_refresh"
            return ["name", "sponsor_name"]
        elif self.is_company and self.sponsor_name:
            # For company if the sponsor name is fill we use it for the url key
            return ["sponsor_name"]
        else:
            return ["name"]

    def _generate_url_key(self, referential, lang):
        url_key = super()._generate_url_key(referential, lang)
        # Add the right prefix for the url key dependendy if it's
        # a company or a person
        if self.is_company:
            return f"integrators/{url_key}"
        else:
            return f"community/{url_key}"

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
        self.sudo()._se_mark_to_update()
        if set(vals.keys()).intersection("name", "sponsor_parent_id"):
            self.sudo().child_ids._se_mark_to_update()
        return res

    # ===== Business logics =====#
    def _get_working_groups(self):
        return self.mail_group_member_ids.mail_group_id.filtered("is_working_group")

    def _get_company_members(self):
        self.ensure_one()
        if self.is_company:
            return (self | self.sponsor_child_ids).child_ids.filtered("is_member")
        else:
            return self.browse()

    def _get_company_contributors(self):
        self.ensure_one()
        if self.is_company:
            return (self | self.sponsor_child_ids).child_ids.filtered(
                lambda s: s.is_contributor
            )
        else:
            return self.browse()
