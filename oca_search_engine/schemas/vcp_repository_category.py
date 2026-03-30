# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel


class VcpRepositoryCategory(StrictExtendableBaseModel):
    name: str
    url_key: str

    @classmethod
    def from_record(cls, odoo_rec):
        return cls.model_construct(
            name=odoo_rec.name, url_key=odoo_rec.env["ir.http"]._slugify(odoo_rec.name)
        )
