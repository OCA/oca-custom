# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..tools.vcp_odoo_module_version_serializer import VcpOdooModuleVersionSerializer


class SeIndex(models.Model):
    _inherit = "se.index"

    serializer_type = fields.Selection(
        selection_add=[
            ("vcp_odoo_module_version_exports", "Odoo Modules"),
        ],
        ondelete={
            "vcp_odoo_module_version_exports": "cascade",
        },
    )

    @api.constrains("model_id", "serializer_type")
    def _check_model(self):
        vcp_odoo_module_version_model = self.env["ir.model"].search(
            [("model", "=", "vcp.odoo.module.version")], limit=1
        )
        for se_index in self:
            if (
                se_index.serializer_type == "vcp_odoo_module_version_exports"
                and se_index.model_id != vcp_odoo_module_version_model
            ):
                raise ValidationError(_("'Serializer Type' must match 'Model'"))

    def _get_serializer(self):
        self.ensure_one()
        if self.serializer_type == "vcp_odoo_module_version_exports":
            return VcpOdooModuleVersionSerializer()
        else:
            return super()._get_serializer()
