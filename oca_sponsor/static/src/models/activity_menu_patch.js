/** @odoo-module */

import {ActivityMenu} from "@mail/core/web/activity_menu";
import {Domain} from "@web/core/domain";
import {patch} from "@web/core/utils/patch";
import {user} from "@web/core/user";

patch(ActivityMenu.prototype, {
    /**
     * @override
     * Since we display the count of both user' and team' activities in the Systray and
     * the drop-down, we update the domain of action opening to show them both in the views
     */
    async executeActivityAction(group, domain, views, context) {
        const team_domain = [["activity_team_user_ids", "=", this.userId]];
        const new_domain = Domain.or([domain, team_domain]).toList();
        context.team_activites = true;
        return super.executeActivityAction(group, new_domain, views, context);
    },
    updateTeamActivitiesContext() {
        /* Needed so `_search_my_activity_date_deadline` renders team activities */
        super.updateTeamActivitiesContext();
        user.updateContext({team_activities: true});
    },
    onBeforeOpen() {
        super.onBeforeOpen();
        user.updateContext({team_activities: true});
    },
});
