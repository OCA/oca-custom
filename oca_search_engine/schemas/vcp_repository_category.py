# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel


class VcpRepositoryCategoryLight(StrictExtendableBaseModel):
    name: str
    url_key: str

    @classmethod
    def from_record(cls, record):
        record._update_url_key(lang=record.env.context.get("lang"))
        return cls.model_construct(
            name=record.name,
            url_key=record.url_key,
        )


class VcpRepositoryCategory(VcpRepositoryCategoryLight):
    id: int
    short_description: str | None
    description: str | None

    @classmethod
    def from_record(cls, record):
        obj = super().from_record(record)
        obj.id = record.id
        obj.short_description = record.short_description or None
        obj.description = record.description or None
        return obj
