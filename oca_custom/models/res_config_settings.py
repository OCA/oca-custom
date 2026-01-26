from odoo import api, fields, models

PARAM_PREFIX = "oca_membership_channel_sync."


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    member_tag_id = fields.Many2one(
        "res.partner.category",
        string="Member tag",
        help="Partner tag that marks Members.",
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env["ir.config_parameter"].sudo()
        val = ICP.get_param(PARAM_PREFIX + "member_tag_id")
        res.update(
            member_tag_id=int(val) if val and val.isdigit() else False,
        )
        return res

    def set_values(self):
        res = super().set_values()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param(
            PARAM_PREFIX + "member_tag_id",
            str(self.member_tag_id.id) if self.member_tag_id else "",
        )
        return res
