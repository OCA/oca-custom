# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

class MailActivity(models.Model):
    _inherit = ["mail.activity"]

    def action_done(self):
        self._cancel_sibling_sponsor_reviewals()
        return super().action_done()
    
    def action_cancel(self):
        self._cancel_sibling_sponsor_reviewals()
        return super().action_cancel()

    def _cancel_sibling_sponsor_reviewals(self):
        """When 1 user review a sponsor, cancel sibling activities for the other reviewers"""
        if self._context.get("skip_cancel_sibling_sponsor"):
            return
        
        activities = self.filtered(lambda x: x.res_model == "res.partner")
        if activities:
            activity_type = self.env.ref("oca_sponsor.mail_activity_review_sponsor_oca")
            partners = self.env["res.partner"].browse(activities.mapped("res_id"))
            siblings = partners.sudo().activity_ids.filtered( # 'sudo' because activities of other users
                lambda x: x.activity_type_id == activity_type
            ) - self
            siblings.with_context(skip_cancel_sibling_sponsor=True).action_cancel()
