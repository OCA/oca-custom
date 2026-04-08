# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..tools import (
    CompanySerializer,
    PersonSerializer,
    # PscSerializer,
    VcpOdooModuleVersionSerializer,
)


class SeIndex(models.Model):
    _inherit = "se.index"

    serializer_type = fields.Selection(
        selection_add=[
            ("vcp_odoo_module_version_exports", "Odoo Modules"),
            ("companies_exports", "Companies (sponsors & integrators)"),
            ("persons_exports", "Persons (members & contributors)"),
            # ("pscs_exports", "PSCs (Project Steering Teams)"),
        ],
        ondelete={
            "vcp_odoo_module_version_exports": "cascade",
            "companies_exports": "cascade",
            "persons_exports": "cascade",
            # "pscs_exports": "cascade",
        },
    )

    @api.constrains("model_id", "serializer_type")
    def _check_model(self):
        mapped_models = {
            "companies_exports": "res.partner",
            "persons_exports": "res.partner",
            # "pscs_exports": "vcp.oca.psc",
            "vcp_odoo_module_version_exports": "vcp.odoo.module.version",
        }
        for se_index in self:
            model = mapped_models.get(se_index.serializer_type)
            if model and se_index.model_id != self.env["ir.model"]._get(model):
                raise ValidationError(_("'Serializer Type' must match 'Model'"))

    def _get_serializer(self):
        self.ensure_one()
        mapped_serializer = {
            "companies_exports": CompanySerializer(),
            "persons_exports": PersonSerializer(),
            # "pscs_exports": PscSerializer(),
            "vcp_odoo_module_version_exports": VcpOdooModuleVersionSerializer(),
        }
        return mapped_serializer.get(self.serializer_type) or super()._get_serializer()
