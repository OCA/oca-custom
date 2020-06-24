# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade  # pylint: disable=W7936


def convert_image_attachments(env):
    mapping = {
        "project.project": "image",
    }
    for model, field in mapping.items():
        Model = env[model]
        attachments = env["ir.attachment"].search(
            [
                ("res_model", "=", model),
                ("res_field", "=", field),
                ("res_id", "!=", False),
            ]
        )
        for attachment in attachments:
            Model.browse(attachment.res_id).image_1920 = attachment.datas


@openupgrade.migrate()
def migrate(env, version):
    convert_image_attachments(env)
