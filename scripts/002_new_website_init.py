#!/usr/bin/env python
# Usage: click-odoo -d <database> 002_new_website_init.py

import click, click_odoo

from click_odoo import odoo

import logging
_logger = logging.getLogger(__file__)

@click.command()
@click_odoo.env_options(default_log_level='info')
def main(env):
    _init_membership_category_id(env)

def _init_membership_category_id(env):
    _logger.info("_init_membership_category_id: start")

    # 1. Configure product: set `membership_category_id` based on products' name
    mapped_categories = {
        category.name.lower().split(" ")[0]: category
        for category in env["membership.membership_category"].search([])
    }
    products = env["product.product"].with_context(active_test=False).search([("membership", "=", True)])
    for product in products:
        category = None
        for category_name, category in mapped_categories.items():
            if category_name in product.name.lower():
                product.membership_category_id = category
                break

    # 2. On members, set `membership_category_id` based on their last membership line
    members = env["res.partner"].search([("member_lines", "!=", False)])
    for member in members:
        last_line = odoo.fields.first(member.member_lines.sorted("date_to", reverse=True))
        member.membership_category_id = last_line.category_id
    
    _logger.info("_init_membership_category_id: done (%d members)", len(members))

if __name__ == "__main__":
    main()
