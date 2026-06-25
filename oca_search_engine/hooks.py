# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _init_indexing(env)


def _init_indexing(env):
    models = {"res.partner"}  # "vcp.oca.psc"
    for model in models:
        records = env[model].search([])
        records._add_to_oca_search_engine()
        _logger.info("Indexing of %s (%d records) done", model, len(records))
