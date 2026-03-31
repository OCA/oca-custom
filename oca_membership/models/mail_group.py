# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

class MailGroup(models.Model):
    _inherit = ["mail.group"]

    is_working_group = fields.Boolean(
        string="Is a Working Group",
        default=False,
        help="Working Group are visible on the website page, on members profile.",
    )
