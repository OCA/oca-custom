# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel
from .vcp_repository_category import VcpRepositoryCategory


class VcpRepository(StrictExtendableBaseModel):

    name: str
    url: str
    description: str
    category: VcpRepositoryCategory

    @classmethod
    def from_record(cls, odoo_rec):
        return cls.model_construct(
            name=odoo_rec.name,
            description=odoo_rec.description,
            url=odoo_rec._get_repository_url(),
            category=VcpRepositoryCategory.from_record(odoo_rec.category_id)
        )
