# -*- coding: utf-8 -*-
# Copyright (C) Odoo Community Association (OCA)
# @author: Alexandre Fayolle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    members = fields.Many2many(
        'res.users',
        'project_user_rel',
        'project_id',
        'uid',
        'Project Members'
    )
