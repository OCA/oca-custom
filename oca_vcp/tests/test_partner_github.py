from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPartnerGithub(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.member = cls.env["res.partner"].create(
            [
                {
                    "name": "Happy Member",
                    "is_company": False,
                    "country_id": cls.env.ref("base.fr").id,
                }
            ]
        )
        cls.member_2 = cls.env["res.partner"].create(
            [
                {
                    "name": "Super Happy Member",
                    "is_company": False,
                    "country_id": cls.env.ref("base.fr").id,
                }
            ]
        )
        cls.github = cls.env.ref("vcp_github.vcp_github_host")

    def test_set_github_login(self):
        self.member.github_main_login = "johndoe"
        self.assertEqual(len(self.member.vcp_user_ids), 1)
        self.assertEqual(self.member.vcp_user_ids.external_id, "johndoe")
        self.assertTrue(self.member.vcp_user_ids.is_github_main_login)

    def test_unset_github_login(self):
        self.member.github_main_login = "johndoe"
        self.assertEqual(len(self.member.vcp_user_ids), 1)
        self.member.github_main_login = ""
        self.assertFalse(self.member.vcp_user_ids)

    def test_set_existing_github_login(self):
        self.env["vcp.user"].create(
            {
                "name": "johndoe",
                "external_id": "johndoe",
                "host_id": self.github.id,
                "partner_id": self.member_2.id,
            }
        )
        with self.assertRaises(UserError):
            self.member.github_main_login = "johndoe"

    def test_set_used_github_login(self):
        vcp_user = self.env["vcp.user"].create(
            {
                "name": "johndoe",
                "external_id": "johndoe",
                "host_id": self.github.id,
            }
        )
        self.member.github_main_login = "johndoe"
        self.assertEqual(vcp_user.partner_id, self.member)

    def test_change_main_and_with_sync(self):
        vcp_user = self.env["vcp.user"].create(
            {
                "name": "foobar",
                "external_id": "foobar",
                "host_id": self.github.id,
                "partner_id": self.member.id,
                "is_github_main_login": True,
                "sync_image_to_partner": True,
            }
        )
        self.assertEqual(self.member.github_main_login, "foobar")
        self.assertTrue(self.member.github_sync_avatar)
        self.member.github_main_login = "johndoe"
        new_vcp_user = self.member.vcp_user_ids.filtered(
            lambda s, vcp_user=vcp_user: s != vcp_user
        )
        self.assertEqual(len(new_vcp_user), 1)
        self.assertEqual(new_vcp_user.external_id, "johndoe")
        self.assertTrue(new_vcp_user.sync_image_to_partner)

    def test_sync_avatar(self):
        self.member.github_main_login = "johndoe"
        self.member.github_sync_avatar = True
        self.assertTrue(self.member.vcp_user_ids.sync_image_to_partner)
        self.member.github_sync_avatar = False
        self.assertFalse(self.member.vcp_user_ids.sync_image_to_partner)
