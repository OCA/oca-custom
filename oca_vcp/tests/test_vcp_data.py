# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.fields import Date

from odoo.addons.base.tests.common import TransactionCase


class TestOCAVcpPartner(TransactionCase):
    @classmethod
    def _create_organization(cls, name):
        partner = cls.env["res.partner"].create({"name": name})
        return cls.env["vcp.organization"].create(
            {
                "name": name,
                "external_id": name.lower(),
                "host_id": cls.host.id,
                "partner_id": partner.id,
            }
        )

    @classmethod
    def _create_vcp_user(cls, name, login):
        partner = cls.env["res.partner"].create({"name": name})
        return cls.env["vcp.user"].create(
            {
                "name": name,
                "external_id": login,
                "host_id": cls.host.id,
                "partner_id": partner.id,
            }
        )

    @classmethod
    def _create_plateform(cls):
        cls.host_type = cls.env["vcp.host.type"].create(
            {
                "name": "Dummy",
                "code": "dummy",
                "code_kind": "dummy",
            }
        )
        cls.host = cls.env["vcp.host"].create(
            {
                "name": "Dummy Platform",
                "type_id": cls.host_type.id,
            }
        )
        cls.platform = cls.env["vcp.platform"].create(
            {
                "name": "oca",
                "short_description": "OCA",
                "description": "OCA",
                "host_id": cls.host.id,
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_plateform()

        # Create Enric / Dixmit
        cls.org_01 = cls._create_organization("Dixmit")
        cls.user_01 = cls._create_vcp_user("Enric Tobella", "etobella")
        cls.user_01.partner_id.parent_id = cls.org_01.partner_id

        # Create Yannick / C2C - Acsone case
        cls.org_02 = cls._create_organization("Acsone")
        cls.user_02 = cls._create_vcp_user("Yannick Payot", "yvaucher")
        cls.user_02.partner_id.parent_id = cls.org_02.partner_id

        date = Date.today()
        cls.repository = cls.env["vcp.repository"].create(
            {
                "name": "wms",
                "description": "OCA/wms",
                "platform_id": cls.platform.id,
                "from_date": date,
            }
        )
        cls.pull_request_01 = cls.env["vcp.request"].create(
            {
                "external_id": 42,
                "name": "Test PR",
                "repository_id": cls.repository.id,
                "user_id": cls.user_01.id,
                "organization_id": cls.org_01.id,
                "created_at": date,
                "closed_at": date,
                "is_merged": True,
            }
        )

    def test_comment_organization(self):
        comment = self.env["vcp.comment"].create(
            {
                "external_id": 42,
                "body": "Test Comment from Yannick to Enric",
                "request_id": self.pull_request_01.id,
                "user_id": self.user_02.id,
                "created_at": Date.today(),
            }
        )
        partner_org_02 = self.user_02.partner_id.parent_id
        self.assertEqual(comment.partner_organization_id, partner_org_02)
        self.assertEqual(self.user_02.partner_id.vcp_comments, 1)
        self.assertEqual(partner_org_02.vcp_comments, 1)

    def test_review_organization(self):
        review = self.env["vcp.review"].create(
            {
                "external_id": 42,
                "body": "Test Review From Yannick to Enric",
                "state": "APPROVED",
                "request_id": self.pull_request_01.id,
                "user_id": self.user_02.id,
                "submitted_at": Date.today(),
            }
        )
        partner_org_02 = self.user_02.partner_id.parent_id
        self.assertEqual(review.partner_organization_id, partner_org_02)
        self.assertEqual(self.user_02.partner_id.vcp_reviews, 1)
        self.assertEqual(partner_org_02.vcp_reviews, 1)

    def test_organization_history(self):
        partner_org_02 = self.org_02.partner_id
        partner_org_03 = self._create_organization("Camptocamp").partner_id

        self.user_02.partner_id.write(
            {
                "organization_history_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_organization_id": partner_org_03.id,
                            "date_start": "2011-01-01",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_organization_id": partner_org_02.id,
                            "date_start": "2025-07-01",
                        },
                    ),
                ]
            }
        )

        review = self.env["vcp.review"].create(
            {
                "external_id": 42,
                "body": "Test Review From Yannick to Enric",
                "state": "APPROVED",
                "request_id": self.pull_request_01.id,
                "user_id": self.user_02.id,
                "submitted_at": "2020-01-01 00:00:00",
            }
        )
        self.assertEqual(review.partner_organization_id, partner_org_03)

        review2 = self.env["vcp.review"].create(
            {
                "external_id": 43,
                "body": "Test Review From Yannick to Enric",
                "state": "APPROVED",
                "request_id": self.pull_request_01.id,
                "user_id": self.user_02.id,
                "submitted_at": "2026-01-01 00:00:00",
            }
        )
        self.assertEqual(review2.partner_organization_id, partner_org_02)
