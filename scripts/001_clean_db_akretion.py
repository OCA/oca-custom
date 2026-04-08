#!/usr/bin/env python
# Usage: click-odoo -d <database> 001_clean_db_akretion.py

import logging

import click
import click_odoo

_logger = logging.getLogger(__name__)


@click.command()
@click_odoo.env_options(default_log_level="debug")
def main(env):
    _01_fix_orphans_views_manual(env)
    _02_uninstall_modules(env)

    # clean DB space (takes some time)
    _logger.warning("Start of 'VACUUM FULL;'")
    env.execute("""
        VACUUM FULL;
    """)
    _logger.warning("End of 'VACUUM FULL;'")


def _01_fix_orphans_views_manual(env):
    _logger.warning("_01_fix_orphans_views_manual")

    # Loyalty: remove orphans view blocking install of 'oca_custom'
    env.execute("""
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
    env.execute("""
        DROP TABLE IF EXISTS x_bi_sql_view_module_version_creation_date;
    """)
    env["ir.module.module"].search(
        [("name", "=", "sql_request_abstract")]
    ).button_immediate_uninstall()
