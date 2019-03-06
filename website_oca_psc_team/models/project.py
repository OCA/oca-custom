# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import image_resize_images


class ProjectProject(models.Model):
    _inherit = 'project.project'

    description = fields.Html()

    github_repository_ids = fields.One2many(
        comodel_name='project.github.repository',
        inverse_name='project_id',
        string='Github Repositories')

    image = fields.Binary(
        attachment=True,
        help="This field holds the image used for"
             " project, limited to 1024x1024px")

    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of project. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. ")

    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of project. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. ")

    @api.model
    def create(self, vals):
        image_resize_images(vals)
        return super(ProjectProject, self).create(vals)

    @api.multi
    def write(self, vals):
        image_resize_images(vals)
        return super(ProjectProject, self).write(vals)
