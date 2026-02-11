# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from types import SimpleNamespace
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class _FakePull:
    def __init__(self, sha):
        self.merged = True
        self.head = SimpleNamespace(sha=sha)
        # Match typical PyGithub shape: datetime
        self.merged_at = datetime.datetime(2018, 7, 10, 12, 1, 59)


class _FakeCommit:
    def __init__(self, files):
        # PyGithub commit.files items have .filename
        self.files = [SimpleNamespace(filename=f) for f in files]


class _FakeRepo:
    def __init__(self, sha, files):
        self._sha = sha
        self._files = files

    def get_pull(self, _number):
        return _FakePull(self._sha)

    def get_commit(self, _sha):
        return _FakeCommit(self._files)


class _FakeEvent:
    def __init__(self, repo, org_login="OCA"):
        self.type = "PullRequestEvent"
        self.org = SimpleNamespace(login=org_login)
        self.repo = repo
        # The production code reads gh_event.payload["action"] and PR number
        self.payload = {
            "action": "opened",
            "pull_request": {"number": 2290},
        }


class _FakeUser:
    def __init__(self, events, name="Contributor 1"):
        self._events = events
        self.name = name

    def get_events(self):
        return self._events


class _FakeGithub:
    def __init__(self, user):
        self._user = user

    def get_user(self, _login):
        return self._user


class TestGithubContributorModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Keep token set to satisfy any code paths that check it,
        # though we patch connector creation anyway.
        cls.env["ir.config_parameter"].sudo().set_param("github.access_token", "test")

        # Ensure "OCA" github org exists (used by get_github_organization())
        GithubOrg = cls.env["github.organization"].sudo()
        if not GithubOrg.search([("github_name", "=", "OCA")], limit=1):
            GithubOrg.create({"name": "OCA", "github_name": "OCA"})

        cls.partner_model = cls.env["res.partner"].sudo()

        # Ensure existing partners are not published
        cls.partner_model.search([]).write({"website_published": False})

        cls.company3 = cls.partner_model.create(
            {
                "name": "Partner 3",
                "is_company": True,
                "website_published": True,
                "github_organization": "company3_github_name",
            }
        )
        cls.contributor1 = cls.partner_model.create(
            {
                "name": "Contributor 1",
                "is_company": False,
                "github_name": "contributor1_github_name",
                "website_published": True,
                "parent_id": cls.company3.id,
            }
        )

        # Create 6 demo product templates linked to 6 odoo.module records
        cls.last_product_template = None
        for i in range(1, 7):
            template = (
                cls.env["product.template"]
                .sudo()
                .create(
                    {
                        "name": f"Prod. Tmpl. demo {i}",
                        "website_published": True,
                    }
                )
            )

            odoo_module = (
                cls.env["odoo.module"]
                .sudo()
                .create(
                    {
                        "technical_name": f"odoo_module{i}",
                    }
                )
            )
            # Link from product side (this field exists in your module)
            template.odoo_module_id = odoo_module.id

            cls.last_product_template = template

    def test_contributor_five_modules(self):
        files = [
            "odoo_module1/readme.rst",
            "odoo_module2/readme.rst",
            "odoo_module3/readme.rst",
            "odoo_module4/readme.rst",
            "odoo_module5/readme.rst",
            "odoo_module6/readme.rst",
        ]
        sha = "385ad61205a8b7e00c97d06cf0e192924e2cc4f7"
        repo = _FakeRepo(sha=sha, files=files)
        fake_user = _FakeUser([_FakeEvent(repo)])
        fake_gh = _FakeGithub(fake_user)

        self.contributor1.write(
            {
                "contributor_module_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_template_id": self.last_product_template.id,
                            "date_pr_merged": "2018-08-12",
                            "partner_id": self.contributor1.id,
                        },
                    )
                ]
            }
        )

        ResPartner = type(self.env["res.partner"])
        with patch.object(ResPartner, "get_github_connector", return_value=fake_gh):
            self.partner_model.cron_create_github_user_module()

        module_lines = (
            self.env["contributor.module.line"]
            .sudo()
            .search([("partner_id", "=", self.contributor1.id)])
        )

        self.assertEqual(len(module_lines), 5)

        names = sorted(module_lines.mapped("product_template_id.technical_name"))
        self.assertListEqual(names, [f"odoo_module{i}" for i in range(1, 6)])
