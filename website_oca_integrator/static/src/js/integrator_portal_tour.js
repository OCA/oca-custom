/* Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('website_oca_integrator.portal', function (require) {
    'use strict';

    var Tour = require("web_tour.tour");
    var base = require("web_editor.base");

    Tour.register('integrator_portal', {
        url: '/my',
        test: true,
        wait_for: base.ready()
        },[
            {
                content: "Click here to edit your details.",
                trigger: "a[href*='/my/account']:contains('Change'):first",
            },
            {
                content: "Enter Phone number.",
                trigger: "input[name='phone']",
                run: "text 123456789",
            },
            {
                content: "Select modules",
                trigger: "#s2id_autogen2",
                run: "text Odoo",
            },
            {
                trigger: ".select2-match",
                auto: true,
                in_modal: false,
            },
            {
                content: "Enter github organization.",
                trigger: "input[name='github_organization']",
                run: "text test_github_organization",
            },
            {
                content: "Write description about your company.",
                trigger: "textarea[name='website_short_description']",
                extra_trigger: "#s2id_autogen1 > ul",
                run: "text My company description"
            },
            {
                content: "Click here to confirm",
                trigger: "button[type='submit']",
            },
            {
                content: "Verify home page is loaded",
                trigger: ".o_portal_my_home",
            },
        ]);
});
