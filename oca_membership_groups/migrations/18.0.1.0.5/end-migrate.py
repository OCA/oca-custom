import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # There was a bug preventing members to be correclty added in the mailing groups
    # => Force re-synchronization for all members to their legitimate mailing groups
    partners = env["res.partner"].sudo().with_context(active_test=False).search([])
    partners._membership_groups_refresh()
