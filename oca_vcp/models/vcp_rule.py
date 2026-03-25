# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import logging
import os
from pathlib import Path

import pypandoc

from odoo import models

_logger = logging.getLogger(__name__)

# see https://github.com/OCA/maintainer-tools/blob/master/tools/gen_addon_readme.py
PANDOC_MARKDOWN_FORMAT = "gfm-raw_html-gfm_auto_identifiers"


class VcpRule(models.Model):
    _inherit = "vcp.rule"

    def _process_rule_odoo_module_prepare_vals(
        self, repository_branch, module_id, manifest_path
    ):
        vals = super()._process_rule_odoo_module_prepare_vals(
            repository_branch, module_id, manifest_path
        )
        module_path = os.path.dirname(manifest_path)
        readme_path = Path(module_path, "readme")
        vals["readme_fragments"] = {}
        if readme_path.exists():
            for item in readme_path.iterdir():
                if item.is_file():
                    filename = item.stem.lower()
                    extension = item.suffix
                    data = item.read_text()
                    if not data:
                        continue
                    if extension == ".md":
                        vals["readme_fragments"][filename] = data
                    elif extension == ".rst":
                        vals["readme_fragments"][filename] = pypandoc.convert_text(
                            data,
                            format="rst",
                            to=PANDOC_MARKDOWN_FORMAT,
                            extra_args=["--shift-heading-level=1"],
                            sandbox=True,
                        )
                    else:
                        _logger.error("Unsupported format in readme path %s".format())

            if Path(module_path, "static/description/icon.png").exists():
                module = self.env["vcp.odoo.module"].browse(module_id)
                repo_name = repository_branch.repository_id.name
                orga_name = repository_branch.repository_id.platform_id.name
                vals["icon_url"] = (
                    f"https://raw.githubusercontent.com/{orga_name}/{repo_name}"
                    f"/refs/heads/{repository_branch.branch_id.name}/"
                    f"{module.name}/static/description/icon.png"
                )
        return vals
