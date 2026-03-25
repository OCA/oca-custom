# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

class ResPartnerGrade(models.Model):
    """Reproduce original data model of 'website_crm_partner_assign',
    but only for membership (grade) and without the CRM part, to free
    this dependency (+ to `base_geolocalize`).
    
    We don't re-define the list/form/search ir.ui.view to avoid conflict
    with native module, in case it is installed in parallel.
    
    *ALTERNATIVE*: create a `membership.sponsorship.category` with a migration
    script copying data from `res.partner.grade`
    """

    _name = "res.partner.grade"
    _order = "sequence"
    _description = "Partner Grade"

    sequence = fields.Integer("Sequence")
    active = fields.Boolean("Active", default=True)
    name = fields.Char("Level Name", translate=True)
