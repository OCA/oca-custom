# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, common, new_test_user

MEMBERSHIP_DURATION = 365
GRACE_DAYS = 90


@common.freeze_time("2026-01-01 09:00:00")
class TestOcaMembershipGroups(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Users
        cls.user = new_test_user(cls.env, "test_user", groups="base.group_user")
        cls.portal_user = new_test_user(
            cls.env, "test_portal", groups="base.group_portal"
        )
        cls.partner = cls.portal_user.partner_id
        cls.partner.email = "test.member@example.com"
        cls.partner2 = cls.env["res.partner"].create(
            [
                {
                    "name": "Test Member 2",
                    "email": "test.member2@example.com",
                }
            ]
        )

        # Membership
        cls.category = cls.env["membership.membership_category"].create(
            [
                {
                    "name": "Test Category",
                }
            ]
        )
        date_from, date_to = cls._get_dates()
        cls.membership_product = cls.env["product.product"].create(
            [
                {
                    "name": "Test Membership Product",
                    "membership": True,
                    "membership_date_from": date_from,
                    "membership_date_to": date_to,
                    "membership_category_id": cls.category.id,
                }
            ]
        )
        cls.mail_group = cls.env["mail.group"].create(
            [
                {
                    "name": "Test Members Group",
                    "alias_name": "test-members-group",
                    "membership_category_ids": cls.category.ids,
                    "grace_days": GRACE_DAYS,
                }
            ]
        )

    # ===== Helpers =====#
    @classmethod
    def _get_dates(cls):
        """Return tuple (date_from, date_to)"""
        today = fields.Date.today()
        return (today, today + timedelta(days=MEMBERSHIP_DURATION))

    @classmethod
    def _promote_member(cls, partner=None, product=None, state="paid"):
        """Create or update membership.line, triggering compute of
        Membership Categories & Mail Groups"""
        membership_lines = (partner or cls.partner).member_lines
        if bool(membership_lines):
            membership_lines.state = state
        else:
            date_from, date_to = cls._get_dates()
            vals = {
                "partner": (partner or cls.partner).id,
                "membership_id": (product or cls.membership_product).id,
                "member_price": 10.0,
                "date_from": date_from,
                "date_to": date_to,
                "state": state,
            }
            cls.env["membership.membership_line"].create([vals])
        cls.env.invalidate_all()  # needed to retrigger compute methods

    @classmethod
    def _destitute_member(cls, partner=None):
        (partner or cls.partner).member_lines.state = "old"
        cls.env.invalidate_all()  # needed to retrigger compute methods

    @classmethod
    def _is_partner_in_group(cls, partner=None, group=None, active_test=True):
        """Return Partners object of a Mail Group"""
        members = (
            (group or cls.mail_group).with_context(active_test=active_test).member_ids
        )
        return (partner or cls.partner) in members.partner_id

    @classmethod
    def _get_members(cls, partner=None, active_test=False):
        return (
            (partner or cls.partner)
            .with_context(active_test=active_test)
            .mail_group_member_ids
        )

    # ===== Tests =====#

    def test_member_auto_add_in_groups(self):
        """Ensure a member is automatically **added** to relevant Mail Groups
        as per its Membership Categories"""
        self.assertFalse(self._is_partner_in_group())  # Initial state
        self._promote_member()
        self.assertTrue(self._is_partner_in_group())

    def test_member_grace_deadline(self):
        """Ensure that when a member loses its role (grace_days > 0):
        1. Its mail.group.member gets a grace_date_start (grace period started)
           and `grace_date_deadline` is computed
        2. It is NOT removed immediately
        3. After grace_days have passed, the CRON removes it"""
        # At destitution: partner still in the mailing list, but in grace period
        self._promote_member()
        self._destitute_member()

        # 1-2: grace period started, still in group
        date_from, _ = self._get_dates()
        self.assertTrue(self._get_members().grace_date_deadline)
        self.assertTrue(self._is_partner_in_group())
        self.assertEqual(
            self._get_members().grace_date_deadline,
            date_from + timedelta(days=GRACE_DAYS),
        )

        # 3. Simulate the CRON: unsubscription
        self._get_members().grace_date_start -= timedelta(days=GRACE_DAYS)
        self.env["res.partner"]._cron_membership_groups_end_grace()
        self.assertFalse(self._is_partner_in_group(active_test=False))

    def test_member_auto_remove_immediately_grace_days_zero(self):
        """Ensure that when grace_days=0, a member losing its role is
        removed immediately (no grace period)"""
        # Start state: put partner in the mailing list with `grace_days=0`
        self.mail_group.grace_days = 0
        self._promote_member()
        self.assertTrue(self._is_partner_in_group())

        # Test: grace period is started and immediatly finished
        self._destitute_member()
        self.assertFalse(self._is_partner_in_group(active_test=False))

    def test_member_stop_grace_period(self):
        """Ensure that if a member renews its membership during the grace period,
        the grace period is cancelled (grace_date_start is reset to False)"""
        # Start state: put in grace
        self._promote_member()
        self._destitute_member()
        self.assertTrue(self._get_members().grace_date_deadline)

        # Renew the membership: grace stops
        self._promote_member()
        self.assertFalse(self._get_members().grace_date_deadline)

    def test_portal_user_unsubscribe_remembers_choice(self):
        """1. When a portal user unsubscribes via the portal flow,
        the mail.group.member is archived (active=False), not deleted.
        2. Re-subscribing via the portal toggles it back to active=True,
        instead of creating a duplicate record."""
        self._promote_member()  # Start state

        # 1. Portal user unsubscribe from the website
        mail_group_portal = self.mail_group.with_context(from_portal=True)
        mail_group_portal._leave_group(self.partner.email, self.partner.id)
        members = self._get_members(active_test=False)
        self.assertTrue(self._is_partner_in_group(active_test=False))
        self.assertTrue(members)
        self.assertFalse(members.active)

        # 2. Portal re-subscribe -> should reactivate, not duplicate
        mail_group_portal._join_group(self.partner.email, self.partner.id)
        self.assertTrue(members.active)
        self.assertTrue(self._is_partner_in_group())

        # No duplicate
        self.assertEqual(1, len(self._get_members(active_test=False)))

    def test_member_no_auto_add_if_unsubscribed(self):
        """Ensure auto-provisioning does NOT re-subscribe a partner who has
        previously unsubscribed manually from the group (archived member)"""
        # Start state: subscribe, but member choose to unsubscribe
        self._promote_member()
        mail_group_portal = self.mail_group.with_context(from_portal=True)
        mail_group_portal._leave_group(self.partner.email, self.partner.id)
        self.assertFalse(self._is_partner_in_group())
        self.assertTrue(self._is_partner_in_group(active_test=False))

        # Play like removing/re-adding the member => it should be kept archived
        self._destitute_member()
        self.assertTrue(self._is_partner_in_group(active_test=False))  # kept
        self._promote_member()
        self.assertFalse(self._is_partner_in_group())  # still not activated
        self.assertTrue(self._is_partner_in_group(active_test=False))  # kept

        # No duplicate
        self.assertEqual(1, len(self._get_members(active_test=False)))
