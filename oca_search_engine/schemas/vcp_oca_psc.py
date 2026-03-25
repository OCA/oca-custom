# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .vcp_odoo_module_version import VcpRepository
from .res_partner_person import PersonBase

from extendable_pydantic import StrictExtendableBaseModel

class Psc(StrictExtendableBaseModel):
    id: int
    name: str
    description: str
    repositories: list[VcpRepository]
    members: list[PersonBase]

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(**cls._model_construct_dict(record))

    @classmethod
    def _model_construct_dict(cls, record):
        return {
            "id": record.id,
            "name": record.name,
            "description": record.description,
            "repositories": record.repository_ids.read(["name", "description"]),
            "members": cls._flatten_list([
                PersonBase.from_record(partner)
                for partner in record.user_ids.partner_id
                if record.user_ids.partner_id
            ]),
        }

    @classmethod
    def _flatten_list(cls, l):
        if any(not isinstance(x, list) for x in l):
            return l
        else:
            return [
                y
                for x in l
                for y in x
            ]
