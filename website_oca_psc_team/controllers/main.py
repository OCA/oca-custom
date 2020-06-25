# Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request

from odoo.addons.http_routing.models.ir_http import unslug


class WebsitePscTeam(http.Controller):
    @http.route(["/psc-teams"], type="http", auth="public", website=True)
    def psc_teams(self, **kwargs):
        values = {"psc_categories": request.env["psc.category"].sudo().search([])}

        return request.render("website_oca_psc_team.psc_teams", values)

    @http.route(["/psc-teams/<project_id>"], type="http", auth="public", website=True)
    def psc_team_project_detail(self, project_id, **kwargs):
        project_name, project_id = unslug(project_id)
        project = request.env["project.project"].sudo().browse(project_id)

        if project.sudo().exists():
            values = {"project": project}

            return request.render("website_oca_psc_team.psc_project_detail", values)

        return self.psc_teams(**kwargs)
