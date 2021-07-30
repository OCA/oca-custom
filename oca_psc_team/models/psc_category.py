# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PscCategory(models.Model):
    _name = "psc.category"
    _order = "sequence"
    _description = "PSC Categories"

    name = fields.Char(
        required=True,
    )

    description = fields.Text(
        required=True,
    )

    sequence = fields.Integer()

    project_ids = fields.One2many(
        comodel_name="project.project", inverse_name="psc_category_id", string="Project"
    )
