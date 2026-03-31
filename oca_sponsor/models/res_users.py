# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResUsers(models.Model):
    _inherit = ["res.users"]

    @api.model
    def _get_activity_groups(self):
        """Team activities are not counted in the Systray, unless user clicks on it
        => Change it to notify the sponsors' reviewers of their team's activity, by
        merging user & team activities so that UI `activityCounter` counts both
        instead of only users.
        Also see `static/src/activity_menu_patch.js` and `mail_activity.xml`"""
        user_activities = super(
            ResUsers, self.with_context(team_activities=False)
        )._get_activity_groups()
        team_activities = super(
            ResUsers, self.with_context(team_activities=True)
        )._get_activity_groups()

        states = ["total"] + [x[0] for x in self.env["mail.activity"]._fields["state"].selection]
        merged_activities = {}
        for activity in user_activities + team_activities:
            model = activity["model"]
            if not model in merged_activities:
                merged_activities[model] = activity
            else:
                for state in states:
                    if state + "_count" in activity:
                        merged_activities[model][state + "_count"] += activity[state + "_count"]

        return list(merged_activities.values())
