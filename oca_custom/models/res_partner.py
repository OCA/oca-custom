# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

PARAM_PREFIX = "oca_membership_channel_sync."
MEMBER_STATES = {"paid", "invoiced", "free"}


class ResPartner(models.Model):
    _inherit = "res.partner"

    github_name = fields.Char(readonly=False)

    def _cfg_id(self, key: str) -> int | None:
        val = self.env["ir.config_parameter"].sudo().get_param(PARAM_PREFIX + key)
        if val and str(val).isdigit():
            return int(val)
        return None

    def _get_sync_config(self):
        delegate_tag_id = self._cfg_id("delegate_tag_id") or 1
        member_tag_id = self._cfg_id("member_tag_id") or 3

        delegate_channel_id = self._cfg_id("delegate_channel_id") or 3
        member_channel_id = self._cfg_id("member_channel_id") or 4

        general_secretary_partner_id = (
            self._cfg_id("general_secretary_partner_id") or 7246
        )

        return {
            "tag2channel": {
                delegate_tag_id: delegate_channel_id,
                member_tag_id: member_channel_id,
            },
            "group_ids": {delegate_channel_id, member_channel_id},
            "general_secretary_partner_id": general_secretary_partner_id,
            "member_tag_id": member_tag_id,
        }

    def _sync_member_tag_from_membership_state(self):
        cfg = self._get_sync_config()
        member_tag = (
            self.env["res.partner.category"].browse(cfg["member_tag_id"]).exists()
        )
        if not member_tag:
            _logger.info(
                "Member tag id=%s not found; skip membership_state tag sync",
                cfg["member_tag_id"],
            )
            return

        to_add = self.filtered(
            lambda p: p.membership_state in MEMBER_STATES
            and member_tag not in p.category_id
        )
        to_remove = self.filtered(
            lambda p: p.membership_state not in MEMBER_STATES
            and member_tag in p.category_id
        )

        if to_add:
            to_add.with_context(skip_membership_channel_sync=True).write(
                {"category_id": [(4, member_tag.id)]}
            )
        if to_remove:
            to_remove.with_context(skip_membership_channel_sync=True).write(
                {"category_id": [(3, member_tag.id)]}
            )

    def _safe_channel_write(self, channel, vals):
        try:
            channel.sudo().write(vals)
            return True
        except Exception:
            _logger.exception(
                "Failed to write discuss channel %s with vals=%s (ignored)",
                channel.ids,
                vals,
            )
            return False

    def _sync_discuss_channels_from_tags(self):
        cfg = self._get_sync_config()
        Channel = self.env["discuss.channel"]
        tag2channel = cfg["tag2channel"]
        group_ids = list(cfg["group_ids"])
        general_secretary_id = cfg["general_secretary_partner_id"]

        channels = Channel.browse(group_ids).exists()
        if not channels:
            _logger.warning(
                "\nNo channels found for configured ids=%s; skip channel sync.\n",
                group_ids,
            )
            return

        tag_model = self.env["res.partner.category"]
        relevant_tags = tag_model.browse(list(tag2channel.keys())).exists()

        for partner in self:
            tags = partner.category_id
            if partner.id == general_secretary_id:
                tags |= relevant_tags

            desired_channel_ids = set()
            for tag in tags:
                chan_id = tag2channel.get(tag.id)
                if chan_id:
                    desired_channel_ids.add(chan_id)

            for chan in channels:
                should_be_member = chan.id in desired_channel_ids

                if "channel_member_ids" in chan._fields:
                    partner_id = partner.id
                    current = chan.channel_member_ids.filtered(
                        lambda m, partner_id=partner_id: m.partner_id.id == partner_id
                    )
                    if should_be_member and not current:
                        self._safe_channel_write(
                            chan,
                            {
                                "channel_member_ids": [
                                    (0, 0, {"partner_id": partner.id})
                                ]
                            },
                        )
                    elif (not should_be_member) and current:
                        self._safe_channel_write(
                            chan, {"channel_member_ids": [(2, current[0].id)]}
                        )
                else:
                    field = "channel_partner_ids"
                    if field not in chan._fields:
                        _logger.warning(
                            "\nChannel model %s has no member field we know; skip.\n",
                            chan._name,
                        )
                        continue

                    is_member = partner in chan[field]
                    if should_be_member and not is_member:
                        self._safe_channel_write(chan, {field: [(4, partner.id)]})
                    elif (not should_be_member) and is_member:
                        self._safe_channel_write(chan, {field: [(3, partner.id)]})

    def action_membership_sync(self):
        self._sync_member_tag_from_membership_state()
        self._sync_discuss_channels_from_tags()
        return True

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get("skip_membership_channel_sync"):
            return res

        if "membership_state" in vals:
            self._sync_member_tag_from_membership_state()

        if "category_id" in vals:
            self._sync_discuss_channels_from_tags()

        return res
