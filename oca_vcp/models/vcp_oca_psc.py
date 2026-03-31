# Copyright 2026 Akretion (https://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, Command

INDEX_PSCS = "oca_search_engine.oca_typesense_index_pscs"


class VcpOcaPsc(models.Model):
    _name = "vcp.oca.psc"
    _inherit = ["se.indexable.record"]
    _description = "Project Steering Team"

    name = fields.Char()
    description = fields.Char()
    repository_ids = fields.Many2many(
        comodel_name="vcp.repository",
        relation="vcp_oca_psc_repository_rel",
        column1="team_id",
        column2="repository_id",
    )
    user_ids = fields.Many2many(
        comodel_name="vcp.user",
        relation="vcp_oca_psc_user_rel",
        column1="team_id",
        column2="user_id",
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name)",
            "Name must be unique.",
        )
    ]

    #===== CRUD =====#    
    def _add_to_oca_search_engine(self):
        """Add records or update fields in the index"""
        self._add_to_index(self.env.ref(INDEX_PSCS))
        return self
    
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)._add_to_oca_search_engine()

    def write(self, vals):
        res = super().write(vals)
        self._add_to_oca_search_engine()
        return res

    #===== Logics =====#
    def _update_from_source(self, branch, mapped_pscs):
        """Update Odoo data from data source"""
        # Fetch data
        pscs = self.search([])
        pscs_by_name = pscs.grouped("name")
        platform = branch.repository_id.platform_id
        host_users = self.env["vcp.user"].search(
            [("host_id", "=", platform.host_id.id)],
        )

        # Unlink unfound teams
        pscs.filtered(lambda x: x.name not in mapped_pscs).unlink()

        # Create new teams, update existings
        vals_list = []
        for name, psc_dict in mapped_pscs.items():
            vals = self._prepare_team_vals(name, psc_dict, host_users, platform)
            psc = pscs_by_name.get(name)
            if psc:
                psc.write(vals)
            else:
                vals_list.append(vals)
        if vals_list:
            pscs.create(vals_list)


    def _prepare_team_vals(self, name, psc_dict, host_users, platform):
        """Return `vals` for create
        Also create any missing users, since one could be PSC with no contribution
        For Repo: assumes they already exist (created by another rule)"""
        # Users
        psc_logins = set(psc_dict.get("members", []) + psc_dict.get("representatives", []))
        psc_users = host_users.filtered(lambda x: x.name in psc_logins)
        to_create = psc_logins - set(psc_users.mapped("name"))
        created_ids = [platform.host_id._get_user(login) for login in to_create]
        psc_users |= self.env["vcp.user"].browse(created_ids)
        
        # Repositories
        psc_repos_names = psc_dict.get("repos", {}).keys()
        psc_repos = platform.repository_ids.filtered(
            lambda x: x.name in psc_repos_names
        )

        return {
            "name": name,
            "description": psc_dict["name"],
            "user_ids": [Command.set(psc_users.ids)],
            "repository_ids": [Command.set(psc_repos.ids)],
        }
