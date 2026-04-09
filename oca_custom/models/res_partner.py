# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

PARAM_PREFIX = "oca_membership_channel_sync."
MEMBER_STATES = {"paid"}


class ResPartner(models.Model):
    _inherit = "res.partner"

    github_name = fields.Char(readonly=False, copy=False)

    # def _cfg_id(self, key: str) -> int | None:
    #     val = self.env["ir.config_parameter"].sudo().get_param(PARAM_PREFIX + key)
    #     if val and str(val).isdigit():
    #         return int(val)
    #     return None

    # def _get_member_tag(self):
    #     member_tag_id = self._cfg_id("member_tag_id") or 3
    #     tag = self.env["res.partner.category"].browse(member_tag_id).exists()
    #     if not tag:
    #         _logger.info(
    #             "Member tag id=%s not found; skip membership_state tag sync",
    #             member_tag_id,
    #         )
    #     return tag

    # def _sync_member_tag_from_membership_state(self):
    #     member_tag = self._get_member_tag()
    #     if not member_tag:
    #         return

    #     tag_id = member_tag.id

    #     to_add = self.filtered(
    #         lambda p, tag_id=tag_id: (p.membership_state in MEMBER_STATES)
    #         and (tag_id not in p.category_id.ids)
    #     )
    #     to_remove = self.filtered(
    #         lambda p, tag_id=tag_id: (p.membership_state not in MEMBER_STATES)
    #         and (tag_id in p.category_id.ids)
    #     )

    #     if to_add:
    #         to_add.with_context(skip_membership_channel_sync=True).write(
    #             {"category_id": [(4, tag_id)]}
    #         )
    #     if to_remove:
    #         to_remove.with_context(skip_membership_channel_sync=True).write(
    #             {"category_id": [(3, tag_id)]}
    #         )

    # def action_membership_sync(self):
    #     self._sync_member_tag_from_membership_state()
    #     return True

    # @api.model
    # def _cron_membership_tag_sync(self, batch_size=500):
    #     ICP = self.env["ir.config_parameter"].sudo()

    #     cursor_key = PARAM_PREFIX + "cron_last_partner_id"
    #     last_id = int(ICP.get_param(cursor_key, "0") or 0)

    #     member_tag_id = int(ICP.get_param(PARAM_PREFIX + "member_tag_id", "3") or 3)

    #     partners = self.sudo().search(
    #         [
    #             ("id", ">", last_id),
    #             "|",
    #             ("membership_state", "=", "paid"),
    #             ("category_id", "in", [member_tag_id]),
    #         ],
    #         order="id asc",
    #         limit=batch_size,
    #     )

    #     if not partners:
    #         ICP.set_param(cursor_key, "0")
    #         return True

    #     partners._sync_member_tag_from_membership_state()
    #     ICP.set_param(cursor_key, str(partners[-1].id))
    #     return True

    # def _sync_mail_groups_by_tag_delta(self, before_map):
    #     """
    #     Sync mail.group membership based on changes
    #     in partner tags (category_id).
    #     """
    #     Group = self.env["mail.group"].sudo()
    #     Member = self.env["mail.group.member"].sudo()

    #     groups = Group.search([("partner_tag_id", "!=", False)])
    #     if not groups:
    #         return

    #     # tag_id -> recordset(mail.group)
    #     tag_to_groups = {}
    #     empty_groups = Group.browse()
    #     for g in groups:
    #         tag_to_groups.setdefault(g.partner_tag_id.id, empty_groups)
    #         tag_to_groups[g.partner_tag_id.id] |= g

    #     for partner in self:
    #         before = before_map.get(partner.id, set())
    #         after = set(partner.category_id.ids)

    #         added = after - before
    #         removed = before - after

    #         # ADD memberships & avoid duplicates
    #         if added:
    #             add_groups = empty_groups
    #             for tag_id in added:
    #                 add_groups |= tag_to_groups.get(tag_id, empty_groups)

    #             if add_groups:
    #                 existing = Member.search(
    #                     [
    #                         ("partner_id", "=", partner.id),
    #                         ("mail_group_id", "in", add_groups.ids),
    #                     ]
    #                 )
    #                 existing_group_ids = set(existing.mapped("mail_group_id").ids)

    #                 to_create = [
    #                     {"mail_group_id": gid, "partner_id": partner.id}
    #                     for gid in add_groups.ids
    #                     if gid not in existing_group_ids
    #                 ]
    #                 if to_create:
    #                     Member.create(to_create)

    #         # REMOVE memberships
    #         if removed:
    #             remove_groups = empty_groups
    #             for tag_id in removed:
    #                 remove_groups |= tag_to_groups.get(tag_id, empty_groups)

    #             if remove_groups:
    #                 Member.search(
    #                     [
    #                         ("partner_id", "=", partner.id),
    #                         ("mail_group_id", "in", remove_groups.ids),
    #                     ]
    #                 ).unlink()

    # @api.model_create_multi
    # def create(self, vals_list):
    #     partners = super().create(vals_list)
    #     before_map = {p.id: set() for p in partners}
    #     partners._sync_mail_groups_by_tag_delta(before_map)
    #     return partners

    # def write(self, vals):
    #     before_map = (
    #         {p.id: set(p.category_id.ids) for p in self}
    #         if "category_id" in vals
    #         else {}
    #     )

    #     res = super().write(vals)

    #     if before_map:
    #         self._sync_mail_groups_by_tag_delta(before_map)

    #     if (
    #         not self.env.context.get("skip_membership_channel_sync")
    #         and "membership_state" in vals
    #     ):
    #         self._sync_member_tag_from_membership_state()

    #     return res
