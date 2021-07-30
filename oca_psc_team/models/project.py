# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = ["project.project", "image.mixin"]
    _name = "project.project"

    short_description = fields.Text(
        help="Short description to display it in website PSC teams list page."
    )

    description = fields.Html(
        help="This will be displayed in the project's detail page of PSC team."
    )

    psc_category_id = fields.Many2one(comodel_name="psc.category", string="Category")

    github_repository_ids = fields.One2many(
        comodel_name="github.repository",
        inverse_name="project_id",
        string="Github Repositories",
    )

    @api.constrains("short_description")
    def _check_short_description(self):
        # Project description in website PSC Team list view should be
        # up to 3 lines.
        if self.short_description and len(self.short_description) >= 75:
            raise ValidationError(
                _(
                    "Number of characters must be less than or equal to 75 for "
                    "'Short Description' field."
                )
            )
