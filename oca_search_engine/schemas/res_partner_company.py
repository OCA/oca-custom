# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel

from odoo import exceptions

from .res_partner_common import Country, LogoUrls


class SponsorshipLevel(StrictExtendableBaseModel):
    id: int
    rank: int
    name: str

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            id=record.id,
            name=record.name,
            rank=record.sequence,
        )


class Industry(StrictExtendableBaseModel):
    name: str
    description: str

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            name=record.name,
            description=record.description or "",
        )


class BlogPost(StrictExtendableBaseModel):
    title: str
    teaser: str
    relative_url: str
    cover_url: str

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            title=record.name,
            teaser=record.teaser,
            relative_url=record.website_url,
            cover_url=record._get_background_url(),
        )


class Sponsorship(StrictExtendableBaseModel):
    description_long: str
    description_short: str
    description_why_oca: str
    level: SponsorshipLevel
    industries: list[Industry]
    stories: list[BlogPost]

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            description_long=record.website_long_description or "",
            description_short=record.website_short_description or "",
            description_why_oca=record.website_description_why_sponsoring or "",
            level=SponsorshipLevel.from_record(record.grade_id),
            industries=[
                Industry.from_record(industry)
                for industry in record.sponsor_industry_ids
            ],
            stories=[
                BlogPost.from_record(blog_post) for blog_post in record.blog_post_ids
            ],
        )


class Contact(StrictExtendableBaseModel):
    name: str
    street: str | None = None
    street2: str | None = None
    zip: str | None = None
    city: str | None = None
    state: str | None = None
    country: Country
    phone: str | None = None
    email: str | None = None

    @classmethod
    def from_record(cls, record):
        return cls.model_construct(
            name=record.name,
            street=record.street or None,
            street2=record.street2 or None,
            zip=record.zip or None,
            city=record.city or None,
            state=record.state_id.name or None,
            country=Country.from_record(record.country_id),
            phone=record.phone or None,
            email=record.email or None,
        )


class Company(StrictExtendableBaseModel):
    id: int
    name: str
    email: str
    phone: str
    website: str
    is_integrator: bool
    countries: list[Country]
    logo_urls: LogoUrls | dict
    # github indicators
    contributors_count: int
    collaboration_index: int
    members_count: int
    modules_count: int
    # technical website fields
    url_key: str | None
    redirect_url_key: list[str]
    # sponsorship
    sponsorship: Sponsorship | None
    contacts: list[Contact]

    @classmethod
    def from_record(cls, record):
        if record.sponsor_to_review:
            # This Exception is catched by `recompute_json` and set the bindings'
            # `state` of the to-be-reviewed sponsors in error
            raise exceptions.ValidationError(
                record.env._(
                    "The information of this sponsor were updated and are pending a "
                    "review, thus this operation was blocked."
                )
            )

        # ensure url is up to date
        record._update_url_key(lang=record.env.context.get("lang"))
        members = record._get_company_members()
        contributors = record._get_company_contributors()
        return cls.model_construct(
            id=record.id,
            name=(record.sponsor_name or "").strip() or record.name.strip() or "",
            email=record.email or "",
            phone=record.phone or "",
            website=record.website or None,
            is_integrator=record.is_integrator,
            countries=[
                Country.from_record(country) for country in record.sponsor_country_ids
            ],
            contacts=[
                Contact.from_record(contact)
                for contact in record | record.sponsor_child_ids
            ],
            logo_urls=LogoUrls.from_record(record),
            # github indicators
            contributors_count=len(contributors),
            collaboration_index=record.oca_collaboration_index,
            members_count=len(members),
            modules_count=record.modules_author_count,
            # technical website fields
            url_key=record.is_sponsor and record.url_key or None,
            redirect_url_key=record.redirect_url_key or [],
            # sponsorship
            sponsorship=None
            if not record.is_sponsor
            else Sponsorship.from_record(record),
        )
