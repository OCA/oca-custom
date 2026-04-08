# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import os
import tempfile
from pathlib import Path
from unittest.mock import PropertyMock, patch

from odoo.tests.common import TransactionCase

YML_CONTENT = {
    "psc": """
test-oca-psc:
  members:
    - user-github-login
  name: Human name of the test OCA PSC
""",
    "repo": """
test-repo-name:
  name: Human name of the test repo
  psc: test-oca-psc
  psc_rep: test-oca-psc
""",
}


class TestOcaPscsSearchEngine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.member = cls.env["res.partner"].create(
            [
                {
                    "name": "Happy Member",
                    "is_company": False,
                    "country_id": cls.env.ref("base.fr").id,
                    "free_member": True,
                    "is_published": True,
                }
            ]
        )
        cls.repository_branch = cls.env.ref(
            "oca_search_engine.vcp_branch_repo_oca_maintainer_conf_master"
        )

    def setUp(self):
        super().setUp()
        self._setup_fake_repo()

    def _setup_fake_repo(self):
        """Create fake and temporary YAML files without call to remote URL,
        ensuring they are removed after tests"""
        # Mock the "repository_branch.local_path" so we don't mess PROD data
        tmp_dir = tempfile.TemporaryDirectory()
        patcher = patch.object(
            type(self.repository_branch),
            "local_path",
            new_callable=PropertyMock,
            return_value=tmp_dir.name,
        )
        patcher.start()
        # Ensure file deletion after tests, whether they are successful or fail
        self.addCleanup(patcher.stop)
        self.addCleanup(tmp_dir.cleanup)

        # Create fake .yml files
        base_dirs = ["psc", "repo"]
        for base_dir in base_dirs:
            full_dir = Path(tmp_dir.name) / "conf" / base_dir
            file_path = full_dir / "test.yml"
            os.makedirs(full_dir, exist_ok=True)
            file_path.write_text(YML_CONTENT[base_dir])

    # ==================== Tools ===============

    def _process_rule_oca_psc_update(self):
        """Process all the rule without downloading code and return the created fake PSC
        Instead, the file content in `_setup_fake_repo` will be used."""
        rule = self.env.ref("oca_search_engine.vcp_rule_oca_psc_update")
        path_download_code = patch.object(
            type(self.repository_branch),
            "_download_code",
            new=lambda self, *a, **kw: None,
        )
        with path_download_code:
            rule._process_rule_oca_psc_update(self.repository_branch)
        return self.env["vcp.oca.psc"].search([])

    # ==================== Tests ===============

    def test_psc_download(self):
        """Test .yml reading"""
        psc = self._process_rule_oca_psc_update()
        user = self.env["vcp.user"].search([("name", "=", "user-github-login")])

        self.assertEqual(user.name, "user-github-login")
        self.assertEqual(
            psc.read(["name", "description", "user_ids"]),
            [
                {
                    "id": psc.id,
                    "name": "test-oca-psc",
                    "description": "Human name of the test OCA PSC",
                    "user_ids": user.ids,
                }
            ],
        )
