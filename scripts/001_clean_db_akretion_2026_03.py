#!/usr/bin/env python
import click, click_odoo

import logging
_logger = logging.getLogger(__name__)

@click.command()
@click_odoo.env_options(default_log_level='debug')
def main(env):
    _01_fix_orphans_views_manual(env)
    _02_uninstall_modules(env)
    _03_free_db_space(env)
    _04_remove_duplicate_indexes(env)

    # clean DB space (takes some time)
    _logger.warning("Start of 'VACUUM FULL;'")
    env.execute(f"""
        VACUUM FULL;
    """)
    _logger.warning("End of 'VACUUM FULL;'")

def _01_fix_orphans_views_manual(env):
    _logger.warning("_01_fix_orphans_views_manual")

    # Loyalty: remove orphans view blocking install of 'oca_custom'
    env.execute(f"""
        DELETE FROM ir_ui_view
        WHERE id IN (
            SELECT res_id
            FROM ir_model_data
            WHERE
                module LIKE '%loyalty%'
                AND model = 'ir.ui.view'
        );
    """)


def _02_uninstall_modules(env):
    _logger.warning("_02_uninstall_modules")

    # Remove 'sql_request_abstract': 1 SQL report of 2018 throwing WARNING at Odoo start
    env.execute(f"""
        DROP TABLE IF EXISTS x_bi_sql_view_module_version_creation_date;
    """)
    env['ir.module.module'].search([('name', '=', 'sql_request_abstract')]).button_immediate_uninstall()


def _03_free_db_space(env):
    _logger.warning("_03_free_db_space")

    # 1. Save 22GB of table website_track (80M indexed lines)
    # oca=# SELECT DATE_PART('year', visit_datetime) AS year, COUNT(*) FROM website_track GROUP BY year ORDER BY year;
    # year |  count   
    # ------+----------
    # 2020 |   245950
    # 2021 |  3638629
    # 2022 |  5226488
    # 2023 |  7530616
    # 2024 | 17594311
    # 2025 | 41076026
    # 2026 |  4985794
    env.execute(f"""
        DELETE FROM website_track WHERE visit_datetime < '2025-01-01'; -- 34235994 rows deleted
        DELETE FROM website_track WHERE visit_datetime < '2026-01-01'; -- 41076026 rows deleted (only 2025)
    """)

def _04_remove_duplicate_indexes(env):
    # TODO @arnaudlayec: verify indexes in duplicate
    # look at "def check_indexes"
    # +Odoo log from a "odoo -c oca -u base" + filter on "Keep unexpected index"

    # Remove unused index
    env.execute(f"""
        DROP INDEX IF EXISTS website_track__url_index; -- 3.6 GB
    """)
