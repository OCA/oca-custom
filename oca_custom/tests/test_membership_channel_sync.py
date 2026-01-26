# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMembershipTagSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ICP = cls.env["ir.config_parameter"].sudo()

        cls.tag_member = cls.env["res.partner.category"].create({"name": "Member"})
        cls.partner = cls.env["res.partner"].create({"name": "Partner A"})
        settings = cls.env["res.config.settings"].create({})
        settings.get_values()
        settings.write({"member_tag_id": cls.tag_member.id})
        settings.set_values()

    def test_00_member_tag_setting_roundtrip(self):
        settings = self.env["res.config.settings"].create({})
        vals = settings.get_values()
        self.assertIn("member_tag_id", vals)
        self.assertEqual(vals["member_tag_id"], self.tag_member.id)

    def _set_membership_state_sql(self, partner, state):
        self.env.cr.execute(
            "UPDATE res_partner SET membership_state=%s WHERE id=%s",
            (state, partner.id),
        )
        self.env.invalidate_all()
        return self.env["res.partner"].browse(partner.id)

    def test_01_action_sync_adds_member_tag_when_paid(self):
        partner = self._set_membership_state_sql(self.partner, "paid")
        self.assertNotIn(self.tag_member, partner.category_id)

        partner.action_membership_sync()
        partner.invalidate_recordset()
        self.assertIn(self.tag_member, partner.category_id)

    def test_02_action_sync_removes_member_tag_when_not_paid(self):
        partner = self._set_membership_state_sql(self.partner, "paid")
        partner.action_membership_sync()
        partner.invalidate_recordset()
        self.assertIn(self.tag_member, partner.category_id)

        partner = self._set_membership_state_sql(self.partner, "none")
        partner.action_membership_sync()
        partner.invalidate_recordset()
        self.assertNotIn(self.tag_member, partner.category_id)

    def test_03_cron_sync_reconciles_in_batches(self):
        self.ICP.set_param("oca_membership_channel_sync.cron_last_partner_id", "0")

        partner = self._set_membership_state_sql(self.partner, "paid")
        self.assertNotIn(self.tag_member, partner.category_id)
        self.env["res.partner"]._cron_membership_tag_sync(batch_size=100)

        partner = self.env["res.partner"].browse(self.partner.id)
        self.assertIn(self.tag_member, partner.category_id)

    def test_04_write_hook_syncs_tag_on_membership_state_change(self):
        partner = self.env["res.partner"].browse(self.partner.id)

        # Ensure clean start
        self.assertNotIn(self.tag_member, partner.category_id)

        # This should trigger write() override => add tag
        partner.write({"membership_state": "paid"})
        partner.invalidate_recordset()
        self.assertIn(self.tag_member, partner.category_id)

        # Flip back => should trigger write() override => remove tag
        partner.write({"membership_state": "none"})
        partner.invalidate_recordset()
        self.assertNotIn(self.tag_member, partner.category_id)

    def test_05_settings_get_values_handles_invalid_param(self):
        """Cover: get_values() else branch when ICP value is not a digit."""
        self.ICP.set_param("oca_membership_channel_sync.member_tag_id", "abc")

        settings = self.env["res.config.settings"].create({})
        vals = settings.get_values()

        self.assertIn("member_tag_id", vals)
        self.assertFalse(vals["member_tag_id"])

    def test_06_settings_set_values_clears_param_when_empty(self):
        """Cover: set_values() else branch when no member_tag_id is set."""
        # Put a value first, so we prove it gets cleared
        self.ICP.set_param(
            "oca_membership_channel_sync.member_tag_id", str(self.tag_member.id)
        )

        settings = self.env["res.config.settings"].create({})
        settings.write({"member_tag_id": False})
        settings.set_values()

        val = self.ICP.get_param("oca_membership_channel_sync.member_tag_id")
        self.assertIn(val, ("", False))

    def test_07_cron_resets_cursor_when_no_partners(self):
        """Cover: cron 'no partners' branch (cursor reset to 0)."""
        cursor_key = "oca_membership_channel_sync.cron_last_partner_id"

        # Set cursor past our only partner, so search returns nothing
        self.ICP.set_param(cursor_key, str(self.partner.id))

        # Ensure the only partner won't match the cron domain via paid OR tag
        partner = self._set_membership_state_sql(self.partner, "none")
        partner.write({"category_id": [(3, self.tag_member.id)]})
        partner.invalidate_recordset()

        self.env["res.partner"]._cron_membership_tag_sync(batch_size=100)

        self.assertEqual(self.ICP.get_param(cursor_key), "0")

    def test_08_sync_skips_when_configured_tag_missing(self):
        """Cover: _get_member_tag() 'tag not found' -> early return."""
        self.ICP.set_param("oca_membership_channel_sync.member_tag_id", "999999")

        partner = self._set_membership_state_sql(self.partner, "paid")
        partner.action_membership_sync()
        partner.invalidate_recordset()

        # Should not crash, and should not add our real tag
        self.assertNotIn(self.tag_member, partner.category_id)

    def test_09_cfg_id_returns_none_on_invalid_param(self):
        """Cover: ResPartner._cfg_id() returns None when config is not numeric."""
        self.ICP.set_param("oca_membership_channel_sync.member_tag_id", "abc")

        partner = self.env["res.partner"].browse(self.partner.id)
        self.assertIsNone(partner._cfg_id("member_tag_id"))
