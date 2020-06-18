# Copyright 2017-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    members = fields.Many2many(
        comodel_name="res.users",
        relation="project_user_rel",
        column1="project_id",
        column2="uid",
        string="Project Members",
    )
