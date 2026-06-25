# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerGrade(models.Model):
    """Reproduce original data model of 'website_crm_partner_assign',
    but only for membership (grade) and without the CRM part, to free
    this weird dependency (e.g. it implies `base_geolocalize` & other
    non-wanted modules).

    We don't re-define the list/form/search ir.ui.view to avoid conflict
    with native module, in case it is installed in parallel.

    *ALTERNATIVE*: we could create a `membership.sponsorship.category`
    with a migration
    script copying data from `res.partner.grade`
    """

    _name = "res.partner.grade"
    _inherit = "website.published.mixin"
    _order = "sequence"
    _description = "Partner Grade"

    sequence = fields.Integer()
    active = fields.Boolean(default=True)
    name = fields.Char(translate=True)
    partner_weight = fields.Integer(
        "Level Weight",
        default=1,
        help="Gives the probability to assign a lead to this partner "
        "(0 means no assignment).",
    )
    show_industry = fields.Boolean()
