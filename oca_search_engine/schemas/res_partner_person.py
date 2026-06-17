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
    email: str | None
    phone: str | None
    website: str | None
    city: str | None
    address: str | None

    @classmethod
    def from_record(cls, record):
        # When an indiviual belong to a sponsor (so public company information)
        # the company data are used as default if the indivual information
        # are not public
        if (
            record.commercial_partner_id.sponsor_parent_id
            or record.commercial_partner_id.is_sponsor
        ):
            company = record.commercial_partner_id
        else:
            company = record.browse()

        def get_phone(record):
            return record.phone or record.mobile or None

        def get_city(record):
            return " ".join(
                filter(None, [record.city, record.state_id.code, record.zip])
            )

        def get_address(record):
            return "\n".join(filter(None, [record.street, record.street2]))

        return cls.model_construct(
            email=record.is_published_email and record.email or company.email or None,
            phone=record.is_published_phone and get_phone(record) or get_phone(company),
            website=record.is_published_website
            and record.website
            or company.website
            or None,
            city=record.is_published_address and get_city(record) or get_city(company),
            address=record.is_published_address
            and get_address(record)
            or get_address(company),
        )


class ParentCompany(StrictExtendableBaseModel):
    id: int
    name: str
    url_key: str

    @classmethod
    def from_record(cls, record):
        company = (
            record.commercial_partner_id.sponsor_parent_id
            or record.commercial_partner_id
        )

        if not company:
            return {}
        else:
            if company.is_sponsor:
                company._update_url_key(lang=record.env.context.get("lang"))
                url_key = company.url_key
            else:
                url_key = None
            return cls.model_construct(
                id=company.id,
                name=company.sponsor_name or company.name,
                url_key=url_key,
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
