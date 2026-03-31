# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import TypedDict
from .res_partner_company import Country

from extendable_pydantic import StrictExtendableBaseModel

class Contact(TypedDict):
    email: str | None
    phone: str | None
    address: str | None
    city: str | None
    website: str | None

class Team(TypedDict):
    id: int
    name: str
    description: str | None

class Role(TypedDict):
    id: int
    name: str

# class ParentCompany(TypedDict):
#     id: int
#     name: str
#     url_key: str

class PersonBase(StrictExtendableBaseModel):
    """Intermediate 'Person' Class, used in PSC members"""
    id: int
    name: str
    company: dict
    contact: Contact
    country: Country
    # github
    username: str
    avatar_url: str | None

    @classmethod
    def from_record(cls, record):
        # ensure url is up to date
        record._update_url_key(lang=record.env.context.get("lang"))
        return cls.model_construct(**cls._model_construct_dict(record))
    
    @classmethod
    def _model_construct_dict(cls, record):
        return {
            "id": record.id,
            "name": record.name,
            "company": (
                {}
                if not record.parent_id.is_company or not record.commercial_company_name
                else {
                    "id": record.parent_id.id,
                    "name": record.commercial_company_name.strip() or "",
                    "url_key": record.parent_id.url_key,
                }
            ),
            "contact": cls._get_contact(record),
            "country": cls._get_country(record),
            # github, TODO @sebastienbeau
            "username": "record.github_username" or None,
            "avatar_url": "record.github_avatar_url" or None,
            # technical website fields
            "url_key": record.url_key,
        }

    @classmethod
    def _get_contact(cls, record):
        return {
            "email": record.email or "",
            "phone": record.phone or record.mobile or "",
            "website": record.website or "",
            "city": (
                "%(city)s %(state_code)s %(zip)s" % {
                    "city": record.city,
                    "state_code": record.state_id.code,
                    "zip": record.zip,
                }
            ).strip() or "",
            "address": (
                "%(street)s\n%(street2)s" % {
                    "street": record.street,
                    "street2": record.street2,
                }
            ).strip() or "",
        }

    @classmethod
    def _get_country(cls, record):
        return "" if not record.country_id else {
            "code": record.country_id.code,
            "label": record.country_id.name,
        }

class Person(PersonBase):
    # technical website fields
    url_key: str
    # role & psc
    roles: list[Role]
    # psc: int
    # psc_list: list[Team]
    work_group_list: list[Team]
    # github indicators
    collaborator_index: int
    modules_maintained: int
    module_contribution_ids: list[int]

    @classmethod
    def _model_construct_dict(cls, record):
        # psc = record.vcp_user_ids.vcp_oca_psc_ids
        return super()._model_construct_dict(record) | {
            # github indicators
            "translations": 0,
            "collaborator_index": 0,
            "modules_maintained": 0,
            "module_contribution_ids": record.contributor_module_line_ids.ids or [],
            # role
            "roles": cls._get_roles(record),
            # psc (obsolete)
            # "psc": len(psc),
            # "psc_list": psc.read(["name", "description"]),
            "work_group_list": (
                record.mail_group_member_ids.mail_group_id
                .filtered("is_working_group").read(["name", "description"])
            )
        }

    @classmethod
    def _get_roles(cls, record):
        roles = record.membership_category_ids.sorted("sequence", reverse=True).read(["name"])
        if False and record.contributor_count: # TODO review with @sebastienbeau correct field name?
            roles.append({"id": -1, "name": _("Contributor")})
        return roles
