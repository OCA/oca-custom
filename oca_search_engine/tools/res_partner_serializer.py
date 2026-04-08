# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# # License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.search_engine_serializer_pydantic.tools.serializer import (
    PydanticModelSerializer,
)

from ..schemas.res_partner_company import Company
from ..schemas.res_partner_person import Person


class CompanySerializer(PydanticModelSerializer):
    def get_model_class(self):
        return Company

    def serialize(self, record):
        return self.get_model_class().from_record(record).model_dump(mode="json")


class PersonSerializer(PydanticModelSerializer):
    def get_model_class(self):
        return Person

    def serialize(self, record):
        return self.get_model_class().from_record(record).model_dump(mode="json")
