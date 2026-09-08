# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class VcpOdooAuthor(StrictExtendableBaseModel):
    name: str
    url_key: str | None

    @classmethod
    def from_record(cls, odoo_rec):
        partner = odoo_rec.partner_id
        return cls.model_construct(
            name=odoo_rec.name,
            url_key=(
                (partner.is_sponsor or partner.is_integrator)
                and partner.url_key
                or None
            ),
        )
