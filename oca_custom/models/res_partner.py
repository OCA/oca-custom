# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Kept for migration only, to remove once module is uninstalled
    github_name = fields.Char(readonly=False, copy=False)
