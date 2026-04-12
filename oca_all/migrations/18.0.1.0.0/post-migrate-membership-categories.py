# Copyright 2026 Akretion (https://www.akretion.com).
# @author Arnaud LAYEC <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from click_odoo import odoo
from openupgradelib import openupgrade

_logger = logging.getLogger(__file__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """Set Membership Categories on Products, as per their name
    We now need them to manage the Role in the association.
    This scripts helps recomputing the history and define the last active
    'Category' in the association"""

    _logger.info("Membership Category init: start")

    # 1. Configure product: set `membership_category_id` based on products' name
    mapped_categories = {
        category.name.lower().split(" ")[0]: category
        for category in env["membership.membership_category"].search([])
    }
    products = (
        env["product.product"]
        .with_context(active_test=False)
        .search([("membership", "=", True)])
    )
    for product in products:
        category = None
        for category_name, category in mapped_categories.items():
            if category_name in product.name.lower():
                product.membership_category_id = category
                break

    # 2. On members, set `membership_category_id` based on their last membership line
    members = env["res.partner"].search([("member_lines", "!=", False)])
    for member in members:
        last_line = odoo.fields.first(
            member.member_lines.sorted("date_to", reverse=True)
        )
        member.membership_category_id = last_line.category_id

    _logger.info("Membership Category init: done (%d members)", len(members))
