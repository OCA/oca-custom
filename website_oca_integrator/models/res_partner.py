# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_integrator = fields.Boolean(
        string="Integrator",
        compute="_compute_integrator",
        store=True,
    )

    member_count = fields.Integer(
        string="Number of members",
        compute="_compute_member_count",
        store=True,
    )

    implemented_date = fields.Date()

    sponsorship_line_ids = fields.One2many(
        string="Sponsorship Activities",
        comodel_name="sponsorship.line",
        inverse_name="partner_id",
    )

    @api.depends(
        "child_ids",
        "child_ids.membership_state",
        "child_ids.parent_id",
    )
    def _compute_integrator(self):
        """
        Integrators are partners who have any contact a current OCA membership.
        """
        for partner in self:
            partner.is_integrator = any(
                child.membership_state == "paid" for child in partner.child_ids
            )

    @api.depends("child_ids.membership_state", "child_ids.parent_id")
    def _compute_member_count(self):
        member_data = self.read_group(
            domain=[("parent_id", "in", self.ids), ("membership_state", "=", "paid")],
            fields=["parent_id"],
            groupby=["parent_id"],
        )
        member_mapped_data = {
            item["parent_id"][0]: item["parent_id_count"] for item in member_data
        }
        for partner in self:
            partner.member_count = member_mapped_data.get(partner.id, 0)
