# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class VcpOdooMaintainer(StrictExtendableBaseModel):
    name: str
    github_user: str
    avatar_url: str
    url_key: str

    @classmethod
    def from_record(cls, odoo_rec):
        return cls.model_construct(
            name=odoo_rec.name,
            github_user=odoo_rec.external_id,
            avatar_url=odoo_rec.avatar_url,
            url_key=(
                odoo_rec.partner_id.website_published
                and odoo_rec.env["ir.http"]._slugify(odoo_rec.partner_id.name)
            )
            or "",
        )
