def migrate(cr, version):
    """Remove legacy stored field `is_membership_invoice`, which comes from
    an old module 'membership_delegated_partner_line', so that it becomes
    a computed field"""
    cr.execute("""
        ALTER TABLE account_move
            DROP COLUMN IF EXISTS is_project_budget CASCADE;
    """)
