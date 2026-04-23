# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    github_main_login = fields.Char(
        compute="_compute_github_main_login", inverse="_inverse_github_info"
    )
    github_sync_avatar = fields.Boolean(
        compute="_compute_github_sync_avatar",
        inverse="_inverse_github_info",
    )
    oca_collaboration_index = fields.Integer(
        "OCA collaboration index",
        help="This index is based on the last 12 Months. Moving Annual Total (MAT)",
        compute="_compute_oca_collaboration_index",
    )

    @api.depends()
    def _compute_oca_collaboration_index(self):
        for record in self:
            record.oca_collaboration_index = (
                record.vcp_merged_requests
                + record.vcp_reviews
                + record.vcp_created_requests**0.5
                + record.vcp_comments**0.5
            )

    @api.depends("vcp_user_ids.is_github_main_login")
    def _compute_github_main_login(self):
        for record in self:
            record.github_main_login = record.vcp_user_ids.filtered(
                "is_github_main_login"
            ).external_id

    def _inverse_github_info(self):
        # Here be dragons
        # the field github_sync_avatar depend on github_main_login
        # Some case are tricky: if we change the github_main_login we need to
        # keep the value of the github_sync_avatar.
        # Check the test, but it's the main raison of having the same inverse
        # function for the two field

        github = self.env.ref("vcp_github.vcp_github_host")
        for record in self:
            if record.github_main_login:
                github_sync_avatar = record.github_sync_avatar
                user = self.env["vcp.user"].search(
                    [
                        ("external_id", "=", record.github_main_login),
                        ("host_id", "=", github.id),
                    ]
                )
                if user:
                    if not user.partner_id:
                        record.vcp_user_ids.filtered(
                            "is_github_main_login"
                        ).is_github_main_login = False
                        user.partner_id = record
                        user.is_github_main_login = True
                    elif user.partner_id != record:
                        raise UserError(self.env._("This github login is already used"))
                    elif not user.is_github_main_login:
                        record.vcp_user_ids.filtered(
                            "is_github_main_login"
                        ).is_github_main_login = False
                        user.is_github_main_login = True
                else:
                    user_id = github._get_user(record.github_main_login)
                    user = self.env["vcp.user"].browse(user_id)
                    user.write(
                        {
                            "is_github_main_login": True,
                            "partner_id": record.id,
                        }
                    )
                user.sync_image_to_partner = github_sync_avatar
            else:
                record.vcp_user_ids.unlink()

    @api.depends(
        "vcp_user_ids.is_github_main_login",
        "vcp_user_ids.sync_image_to_partner",
    )
    def _compute_github_sync_avatar(self):
        for record in self:
            record.github_sync_avatar = record.vcp_user_ids.filtered(
                "is_github_main_login"
            ).sync_image_to_partner
