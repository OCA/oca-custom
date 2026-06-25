/** @odoo-module */
/* Inspired from `project/static/src/views/project_task_form/project_task_form_controller.js` */

import {FormControllerWithHTMLExpander} from "@resource/views/form_with_html_expander/form_controller_with_html_expander";
import {HistoryDialog} from "@html_editor/components/history_dialog/history_dialog";
import {_t} from "@web/core/l10n/translation";
import {escape} from "@web/core/utils/strings";
import {useService} from "@web/core/utils/hooks";

export class ResPartnerFormController extends FormControllerWithHTMLExpander {
    setup() {
        super.setup();
        this.notifications = useService("notification");
    }

    /**
     * @override
     */
    getStaticActionMenuItems() {
        return {
            ...super.getStaticActionMenuItems(),
            openHistoryDialog: {
                sequence: 50,
                icon: "fa fa-history",
                description: _t("Sponsor Version History"),
                callback: () => this.openSponsorHistoryDialog(),
            },
        };
    }

    async openSponsorHistoryDialog() {
        const record = this.model.root;
        const versionedFieldName = "sponsor_review_data";
        const historyMetadata =
            record.data.html_field_history_metadata?.[versionedFieldName];
        console.log(
            record.data,
            record.data.html_field_history_metadata,
            record.data.html_field_history_metadata?.[versionedFieldName]
        );
        if (!historyMetadata) {
            this.notifications.add(
                escape(_t("The sponsor lacks any past content to review."))
            );
            return;
        }

        this.dialogService.add(HistoryDialog, {
            recordId: record.resId,
            recordModel: this.props.resModel,
            versionedFieldName,
            historyMetadata,
        });
    }
}
