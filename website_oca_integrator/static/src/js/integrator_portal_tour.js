/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("integrator_portal", {
    url: "/my/account",
    test: true,
    steps: () => [
        {
            trigger: "body",
            content: _t("Portal page loaded"),
        },
        {
            trigger: ".module_js_select2, select[name='favourite_module_ids'], select",
            content: _t("Module selector is available"),
        },
    ],
});
