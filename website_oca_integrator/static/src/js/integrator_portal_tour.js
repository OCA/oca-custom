/* Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define("website_oca_integrator.portal", function (require) {
    "use strict";

    var Tour = require("web_tour.tour");
    var base = require("web_editor.base");

    Tour.register(
        "integrator_portal",
        {
            url: "/my/account",
            test: true,
            wait_for: base.ready(),
        },
        [
            {
                trigger: "input[name='phone']",
                run: "text 123456789",
            },
            {
                trigger: "#s2id_autogen2",
                run: "text Prod.",
            },
            {
                trigger: ".select2-match",
                auto: true,
                in_modal: false,
            },
            {
                trigger: "input[name='github_organization']",
                run: "text test_github_organization",
            },
            {
                trigger: "textarea[name='website_short_description']",
                extra_trigger: "#s2id_autogen1 > ul",
                run: "text My company description",
            },
            {
                trigger: "button[type='submit']",
            },
            {
                trigger: ".btn-sm",
            },
        ]
    );
});
