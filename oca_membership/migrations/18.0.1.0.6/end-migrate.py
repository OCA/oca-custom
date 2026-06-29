from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # All memberships must be updated, because of the inherit of
    # `_membership_member_states`
    RP = env["res.partner"].with_context(active_test=False)
    RP.check_membership_all()

    # `is_membership_invoice` already exists in DB because of an old module
    # => it must be recomputed on all records
    AM = env["account.move"].with_context(active_test=False)
    AM.search([])._compute_is_membership_invoice()
