# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectGithubRepository(models.Model):
    _inherit = 'github.repository'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project')
