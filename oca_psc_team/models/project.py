# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import image_resize_images


class ProjectProject(models.Model):
    _inherit = 'project.project'

    short_description = fields.Text(
        help='Short description to display it in website PSC teams list page.'
    )

    description = fields.Html(
        help='This will be displayed in the project\'s detail page of PSC '
             'team.'
    )

    psc_category_id = fields.Many2one(
        comodel_name='psc.category',
        string='Category'
    )

    github_repository_ids = fields.One2many(
        comodel_name='github.repository',
        inverse_name='project_id',
        string='Github Repositories'
    )

    image = fields.Binary(
        attachment=True,
        help='This field holds the image used for'
             ' project, limited to 1024x1024px')

    image_medium = fields.Binary(
        'Medium-sized image', attachment=True,
        help='Medium-sized image of project. It is automatically '
             'resized as a 128x128px image, with aspect ratio preserved.')

    image_small = fields.Binary(
        'Small-sized image', attachment=True,
        help='Small-sized image of project. It is automatically '
             'resized as a 64x64px image, with aspect ratio preserved.')

    @api.model
    def create(self, vals):
        image_resize_images(vals)
        return super(ProjectProject, self).create(vals)

    @api.multi
    def write(self, vals):
        image_resize_images(vals)
        return super(ProjectProject, self).write(vals)

    @api.constrains('short_description')
    def _check_short_description(self):
        # Project description in website PSC Team list view should be
        # up to 3 lines.
        if len(self.short_description) >= 75:
            raise ValidationError(_(
                'Number of characters must be less then or equal to 75 for '
                '\'Short Description\' field.'))
