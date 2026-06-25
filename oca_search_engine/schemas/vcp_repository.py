# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel

from odoo.exceptions import UserError

from .vcp_repository_category import VcpRepositoryCategoryLight


class VcpRepository(StrictExtendableBaseModel):
    name: str
    url: str
    description: str
    category: VcpRepositoryCategoryLight

    @classmethod
    def from_record(cls, odoo_rec):
        if not odoo_rec.category_id:
            raise UserError(
                odoo_rec.env._(
                    "The category on the repository is missing, please fill it"
                )
            )
        return cls.model_construct(
            name=odoo_rec.name,
            description=odoo_rec.description,
            url=odoo_rec._get_repository_url(),
            category=VcpRepositoryCategoryLight.from_record(odoo_rec.category_id),
        )
