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


class LogoUrls(StrictExtendableBaseModel):
    alt: str
    l: str  # noqa: E741
    m: str
    s: str

    @classmethod
    def from_record(cls, record):
        if cls._is_default_avatar(record):
            return {}
        else:
            return cls.model_construct(
                alt=record.name,
                l=cls._get_full_url(record, size=1920),
                m=cls._get_full_url(record, size=512),
                s=cls._get_full_url(record, size=128),
            )

    @classmethod
    def _is_default_avatar(cls, record):
        return not record.image_1920

    @classmethod
    def _get_full_url(cls, record, size):
        return f"{record.get_base_url()}/web/image/res.partner/{record.id}/image_{size}"
