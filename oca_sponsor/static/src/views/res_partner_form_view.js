import {formViewWithHtmlExpander} from "@resource/views/form_with_html_expander/form_view_with_html_expander";
import {registry} from "@web/core/registry";
import {ResPartnerFormController} from "./res_partner_form_controller";

export const ResPartnerFormView = {
    ...formViewWithHtmlExpander,
    Controller: ResPartnerFormController,
};

registry.category("views").add("res_partner_form", ResPartnerFormView);
