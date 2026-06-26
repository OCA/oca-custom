import uuid

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    for website in env["website"].search([]):
        website.altcha_key = str(uuid.uuid4())
        website.altcha_private_key = str(uuid.uuid4())
        website.altcha_timeout = 30
    env.cr.execute("""
        UPDATE ir_config_parameter SET value = ''
        WHERE key IN ('recaptcha_public_key', 'recaptcha_private_key');
    """)
