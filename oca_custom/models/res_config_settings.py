from odoo import api, fields, models

PARAM_PREFIX = "oca_membership_channel_sync."


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    delegate_tag_id = fields.Many2one(
        "res.partner.category",
        string="Delegate tag",
        help="Partner tag that marks Delegates",
    )
    member_tag_id = fields.Many2one(
        "res.partner.category",
        string="Member tag",
        help="Partner tag that marks Members",
    )

    delegate_channel_id = fields.Many2one(
        "discuss.channel",
        string="Delegate channel",
        help="Discuss channel where Delegates should be members",
    )
    member_channel_id = fields.Many2one(
        "discuss.channel",
        string="Member channel",
        help="Discuss channel where Members should be members",
    )

    general_secretary_partner_id = fields.Many2one(
        "res.partner",
        string="General secretary partner",
        help="Partner that must be member of all channels implied by tags",
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env["ir.config_parameter"].sudo()

        def _get_m2o(model, key):
            val = ICP.get_param(PARAM_PREFIX + key)
            return int(val) if val and val.isdigit() else False

        res.update(
            delegate_tag_id=_get_m2o("res.partner.category", "delegate_tag_id"),
            member_tag_id=_get_m2o("res.partner.category", "member_tag_id"),
            delegate_channel_id=_get_m2o("discuss.channel", "delegate_channel_id"),
            member_channel_id=_get_m2o("discuss.channel", "member_channel_id"),
            general_secretary_partner_id=_get_m2o("res.partner", "general_secretary_partner_id"),
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env["ir.config_parameter"].sudo()

        def _set(key, record):
            ICP.set_param(PARAM_PREFIX + key, str(record.id) if record else "")

        _set("delegate_tag_id", self.delegate_tag_id)
        _set("member_tag_id", self.member_tag_id)
        _set("delegate_channel_id", self.delegate_channel_id)
        _set("member_channel_id", self.member_channel_id)
        _set("general_secretary_partner_id", self.general_secretary_partner_id)
