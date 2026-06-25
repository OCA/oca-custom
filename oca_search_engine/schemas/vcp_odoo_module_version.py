# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel

from .vcp_odoo_author import VcpOdooAuthor
from .vcp_odoo_maintainer import VcpOdooMaintainer
from .vcp_repository import VcpRepository

# Gestion des redirections !


class VcpOdooModuleVersion(StrictExtendableBaseModel):
    id: int
    name: str
    techname: str
    repo: VcpRepository
    version: str
    serie: str
    dependencies: list
    license: str
    summary: str
    development_status: str
    authors: list[VcpOdooAuthor]
    github_url: str
    runboat_url: str
    readme_fragments: dict
    maintainers: list[VcpOdooMaintainer]
    icon_url: str
    must_have: bool
    url_key: str
    redirect_url_key: list[str]

    @classmethod
    def _get_runboat_url(cls, odoo_rec):
        return (
            "https://runboat.odoo-community.org/webui/builds.html?"
            f"repo=OCA/{odoo_rec.repository_branch_id.repository_id.name}"
            f"&target_branch={odoo_rec.repository_branch_id.branch_id.name}"
        )

    @classmethod
    def from_record(cls, odoo_rec):
        # Ensure url key is up to date
        odoo_rec.module_id._update_url_key(lang=odoo_rec.env.context.get("lang"))
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
            techname=odoo_rec.module_id.name,
            repo=VcpRepository.from_record(odoo_rec.repository_branch_id.repository_id),
            serie=odoo_rec.repository_branch_id.branch_id.name.zfill(4),
            version=odoo_rec.version,
            license=odoo_rec.license,
            summary=odoo_rec.summary,
            development_status=odoo_rec.development_status or "",
            authors=[
                VcpOdooAuthor.from_record(author)
                for author in odoo_rec.author_ids
                if author.name != "Odoo Community Association (OCA)"
            ],
            github_url=odoo_rec.github_url,
            runboat_url=cls._get_runboat_url(odoo_rec),
            readme_fragments=odoo_rec.readme_fragments or {},
            maintainers=[
                VcpOdooMaintainer.from_record(user) for user in odoo_rec.maintainer_ids
            ],
            dependencies=odoo_rec.depends_on_module_ids.mapped("name"),
            icon_url=odoo_rec.icon_url,
            must_have=odoo_rec.module_id.must_have,
            # Note all module version have the same url
            # as version are just variants of the module
            url_key=odoo_rec.module_id.url_key,
            redirect_url_key=odoo_rec.module_id.redirect_url_key or [],
        )
