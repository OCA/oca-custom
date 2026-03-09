# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Oca Search Engine",
    "summary": "Export Public OCA data to search engine",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "custom",
    "website": "https://github.com/OCA/oca-custom",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [
            "extendable_pydantic",
            "pypandoc",
        ],
        "bin": [],
    },
    "depends": [
        "oca_vcp",
        "connector_typesense",
        "search_engine_serializer_pydantic",
        # following dependency are needed by uv to resolve the dep
        # correctly as module are not merged
        "vcp_management",
        "vcp_git",
    ],
    "data": [
        "data/backend_data.xml",
        "data/index_data.xml",
    ],
    "demo": [],
}
