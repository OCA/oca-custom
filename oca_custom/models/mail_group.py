from odoo import fields, models


class MailGroup(models.Model):
    _inherit = "mail.group"

    partner_tag_id = fields.Many2one(
        "res.partner.category",
        string="Partner Tag",
        help="If set, partners having this tag are automatically added/removed"
        " as members of this mail group.",
    )

    # def action_sync_members_from_tag(self):
    #     Member = self.env["mail.group.member"].sudo()
    #     Partner = self.env["res.partner"].sudo()

    #     for group in self:
    #         tag = group.partner_tag_id
    #         if not tag:
    #             continue

    #         tagged_partners = Partner.search([("category_id", "in", [tag.id])])
    #         tagged_ids = set(tagged_partners.ids)

    #         existing_members = group.member_ids.sudo()
    #         existing_partner_ids = set(existing_members.mapped("partner_id").ids)

    #         # Add missing members that match tag
    #         to_add_ids = tagged_ids - existing_partner_ids
    #         if to_add_ids:
    #             Member.create(
    #                 [
    #                     {"mail_group_id": group.id, "partner_id": pid}
    #                     for pid in to_add_ids
    #                 ]
    #             )

    #         # Remove members that no longer match tag (authoritative behavior!)
    #         to_remove = existing_members.filtered_domain(
    #             [("partner_id.category_id", "not in", [tag.id])]
    #         )
    #         if to_remove:
    #             to_remove.unlink()

    #     return True

    # def write(self, vals):
    #     res = super().write(vals)
    #     if "partner_tag_id" in vals:
    #         # Run after write so group.partner_tag_id is the new value
    #         self.action_sync_members_from_tag()
    #     return res
