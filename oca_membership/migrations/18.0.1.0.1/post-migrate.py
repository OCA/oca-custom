from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """All memberships must be updated, because of the
    inherit of `_membership_member_states`"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.partner"].check_membership_all()
