# Copyright 2026 Akretion (https://www.akretion.com).
# @author Arnaud LAYEC <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

from odoo.tools import SQL

_logger = logging.getLogger(__file__)

BATCH_SIZE = 1000


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """Lots of avatar are duplicated on `res.partner`, and stored 'in hard' in database
    though they are default avatar"""

    # 1. Get partners with similar avatar (by checksum)
    res = env.execute_query(
        SQL("""
        SELECT res_id
        FROM ir_attachment
        WHERE checksum IN (
            SELECT checksum -- , COUNT(id), MAX(res_id)
            FROM ir_attachment
            WHERE res_model = 'res.partner' AND res_field = 'image_1920'
            GROUP BY checksum
            HAVING COUNT(id) >= 2
            ORDER BY COUNT(id) DESC
        )
        AND res_model = 'res.partner'
    """)
    )
    partner_ids = [y for x in res for y in x]
    attachments = env["ir.attachment"].search(
        [
            ("res_model", "=", "res.partner"),
            ("res_field", "in", ("image_1920", "image_1024", "image_256", "image_128")),
            ("res_id", "in", partner_ids),
        ]
    )
    # Remove all duplicated attachment in background
    attachments.delayable().unlink().split(size=BATCH_SIZE).delay()
    _logger.info(
        "Avatar cleaning launch in background: %d partners will be cleaned.",
        len(partner_ids),
    )
