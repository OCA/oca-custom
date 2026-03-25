# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import TypedDict

from extendable_pydantic import StrictExtendableBaseModel

class Country(TypedDict):
    code: str
    label: str

class LogoUrls(TypedDict):
    alt: str
    l: str
    m: str
    s: str

class SponsorLevel(TypedDict):
    id: int
    rank: int
    name: str

class Industry(TypedDict):
    name: str
    description: str | None

class BlogPost(TypedDict):
    title: str
    teaser: str
    relative_url: str
    cover_url: str

class Sponsor(TypedDict):
    description_long: str | None
    description_short: str | None
    description_why_oca: str | None
    level: SponsorLevel
    industries: list[Industry]
    stories: list[BlogPost]

class Company(StrictExtendableBaseModel):
    id: int
    name: str | None
    email: str | None
    phone: str | None
    # editable fields
    website: str | None
    is_integrator: bool
    countries: list[Country]
    logo_urls: LogoUrls
    # github indicators
    contributors_count: int
    contributors_index: int
    members_count: int
    modules_count: int
    # technical website fields
    url_key: str
    redirect_url_key: list[str]
    # sponsorship
    sponsorship: Sponsor | None

    @classmethod
    def from_record(cls, record):
        # ensure url is up to date
        record._update_url_key(lang=record.env.context.get("lang"))
        return cls.model_construct(**cls._model_construct_dict(record))
    
    @classmethod
    def _model_construct_dict(cls, record):
        return {
            "id": record.id,
            "name": record.name.strip() or None,
            "email": record.email or None,
            "phone": record.phone or None,
            # editable fields
            "website": record.website or None,
            "is_integrator": record.is_integrator,
            "countries": [
                {"code": x["code"], "label": x["name"]}
                for x in record.sponsor_country_ids.read(["code", "name"])
            ],
            "logo_urls": {
                "alt": record.name,
                "l": record._get_avatar_url(size=1920),
                "m": record._get_avatar_url(size=512),
                "s": record._get_avatar_url(size=128)
            },
            # github indicators
            # "contributors_count": record.contributors_count or 0,
            # "contributors_index": record.contributors_index or 0,
            # "members_count": record.members_count or 0,
            # "modules_count": record.modules_count or 0,
            "contributors_count": 10,
            "contributors_index": 20,
            "members_count": 30,
            "modules_count": 40,
            # technical website fields
            "url_key": record.url_key,
            "redirect_url_key": record.redirect_url_key,
            # sponsorship
            "sponsorship": None if not record.is_sponsor else {
                "description_long": record.website_long_description or None,
                "description_short": record.website_short_description or None,
                "description_why_oca": record.website_description_why_sponsoring or None,
                "level": {
                    "id": record.grade_id.id,
                    "name": record.grade_id.name,
                    "rank": record.grade_id.sequence,
                },
                "industries": [
                    {
                        "name": industry["name"],
                        "description": industry["description"] or None
                    }
                    for industry in record.sponsor_industry_ids.read(["name", "description"])
                ],
                "stories": [
                    {
                        "title": blog_post.name,
                        "teaser": blog_post.teaser,
                        "relative_url": blog_post.website_url,
                        "cover_url": blog_post._get_background_url(), # can also pass 'height' and 'width'
                    }
                    for blog_post in record.blog_post_ids
                ],
            }
        }
