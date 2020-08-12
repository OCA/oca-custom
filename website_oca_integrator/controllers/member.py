# Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request

from odoo.addons.website_membership.controllers.main import WebsiteMembership


class WebsiteContributorMembership(WebsiteMembership):
    @http.route()
    def partners_detail(self, partner_id, **post):
        """
        Display contributor/member page.
        """
        response = super(WebsiteContributorMembership, self).partners_detail(
            partner_id, **post
        )

        # if contributor/member exist then render page
        # else redirect it to contributor/member list page.
        if response.qcontext.get("partner", False):
            return request.render("website_oca_integrator.members", response.qcontext)
        else:
            return response
