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
    partners = (
        env["res.partner"]
        .browse(set(partner_ids))
        .exists()
        .with_context(prefetch_fields=False)
    )

    # 2. Cleaning duplicated avatars, by batch
    if not partners:
        _logger.info("No partner with duplicate avatar => stop here.")
        return

    partners_count = len(partners)
    _logger.info("Start avatar cleaning: %d partners(s)", partners_count)

    for i in range(0, partners_count, BATCH_SIZE):
        offset = i * BATCH_SIZE
        _logger.info(
            "Batch %d: partners %d to %d...",
            i + 1,
            offset + 1,
            min(offset + BATCH_SIZE, partners_count),
        )

        batch = partners[i : i + BATCH_SIZE]
        batch.image_1920 = False

    _logger.info("Avatar cleaning ended: %d partners cleaned.", partners_count)
