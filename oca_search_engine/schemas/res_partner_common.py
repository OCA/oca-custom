# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class Country(StrictExtendableBaseModel):
    code: str
    label: str

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            code=record.code,
            label=record.name,
        )

class AvatarUrls(StrictExtendableBaseModel):
    alt: str
    l: str
    m: str
    s: str

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            alt=record.name,
            l=record._get_avatar_url(size=1920),
            m=record._get_avatar_url(size=512),
            s=record._get_avatar_url(size=128),
        )
