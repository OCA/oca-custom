from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'


    members = fields.Many2many('res.users', 'project_user_rel', 'project_id', 'uid', 'Project Members')
