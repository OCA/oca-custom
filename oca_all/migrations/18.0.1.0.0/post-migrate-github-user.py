# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    partners = env["res.partner"].search(
        [
            ("github_name", "!=", False),
        ]
    )
    host = env.ref("vcp_github.vcp_github_host")
    for partner in partners:
        env["vcp.user"].create(
            {
                "name": partner.name,
                "external_id": partner.github_name,
                "partner_id": partner.id,
                "host_id": host.id,
            }
        )
