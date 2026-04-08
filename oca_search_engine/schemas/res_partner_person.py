# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel

from odoo import _

from .res_partner_common import Country, LogoUrls


class Role(StrictExtendableBaseModel):
    id: int
    name: str

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            id=record["id"],
            name=record["name"],
        )


class Team(StrictExtendableBaseModel):
    """For Working Groups and PSC"""

    id: int
    name: str
    description: str

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            id=record.id,
            name=record.name,
            description=record.description or "",
        )


class ContactInfo(StrictExtendableBaseModel):
    email: str
    phone: str
    website: str
    city: str
    address: str

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            email=record.is_published_email and record.email or "",
            phone=record.is_published_phone and (record.phone or record.mobile) or "",
            website=record.is_published_website and record.website or "",
            city=(
                f"{record.city} {record.state_id.code} {record.zip}"
                if record.is_published_address
                and any([record.city, record.state_id.code, record.zip])
                else ""
            ),
            address=(
                f"{record.street}\n{record.street2}"
                if record.is_published_address and (record.street or record.street2)
                else ""
            ),
        )


class ParentCompany(StrictExtendableBaseModel):
    id: int
    name: str
    url_key: str

    @classmethod
    def from_record(cls, record):
        if not record.commercial_company_name:
            return {}
        else:
            record.commercial_partner_id._update_url_key(
                lang=record.env.context.get("lang")
            )
            return cls.model_construct(
                id=record.commercial_partner_id.id,
                name=record.commercial_company_name.strip() or "",
                url_key=record.commercial_partner_id.url_key,
            )


class PersonBase(StrictExtendableBaseModel):
    """Intermediate 'Person' Class, used in PSC members"""

    id: int
    name: str
    company: ParentCompany | dict  # allow {}
    contact: ContactInfo
    country: Country | dict

    # github
    github_users: list[str]
    logo_urls: LogoUrls | dict

    @classmethod
    def from_record(cls, record):
        # ensure url is up to date
        record._update_url_key(lang=record.env.context.get("lang"))
        return cls.model_construct(**cls._model_construct_dict(record))

    @classmethod
    def _model_construct_dict(cls, record):
        """Dict to permit inheritance in `Person`"""
        return {
            "id": record.id,
            "name": record.name,
            "company": ParentCompany.from_record(record),
            "contact": ContactInfo.from_record(record),
            "country": (
                Country.from_record(record.country_id) if record.country_id else {}
            ),
            # github
            "github_users": record.vcp_user_ids.mapped("external_id"),
            "logo_urls": LogoUrls.from_record(record),
            # technical website fields
            "url_key": record.url_key,
        }


class Person(PersonBase):
    url_key: str
    roles: list[Role]
    # psc: int
    # psc_list: list[Team]
    work_group_list: list[Team]

    collaboration_index: int
    modules_maintained: int
    module_contribution_ids: list[int]

    @classmethod
    def _model_construct_dict(cls, record):
        # psc = record.vcp_user_ids.vcp_oca_psc_ids
        return super()._model_construct_dict(record) | {
            # github indicators
            "translations": 0,
            "collaboration_index": record.oca_collaboration_index,
            "modules_maintained": record.modules_maintained_count,
            # role
            "roles": cls._get_roles(record),
            # psc (obsolete)
            # "psc": len(psc),
            # "psc_list": psc.read(["name", "description"]),
            "work_group_list": [
                Team.from_record(record) for record in record._get_working_groups()
            ],
        }

    @classmethod
    def _get_roles(cls, record):
        """Add fake role `Contributor` to display it on the website (only)"""
        res = [
            Role.from_record(x)
            for x in record.membership_category_ids.sorted("sequence", reverse=True)
        ]
        if record.is_contributor:
            res.append(
                Role.from_record(
                    {
                        "id": -1,
                        "name": _("Contributor"),
                    }
                )
            )
        return res
