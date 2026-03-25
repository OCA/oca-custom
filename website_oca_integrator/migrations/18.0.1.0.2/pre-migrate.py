# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    view = env.ref(
        "website_oca_integrator.view_crm_partner_geo_form_inherit",
        raise_if_not_found=True,
    )
    if view:
        view.unlink()
