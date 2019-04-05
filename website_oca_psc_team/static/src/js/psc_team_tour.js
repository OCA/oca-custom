/* Copyright 2019 Surekha Technologies (https://www.surekhatech.com)
License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("website_oca_psc_team.psc_team_project_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    tour.register(
        "psc_team_project_tour",
        {
            url: "/psc-teams",
            test: true,
            wait_for: base.ready(),
        },
        [
            {
                content: "Click here to discover project.",
                trigger: "a[href^='/psc-teams/apps-store']",
            },

            {
                content: "Click here to edit project page.",
                extra_trigger: ".well",
                trigger: ".o_menu_systray a[data-action=edit]",
            },

            {
                content: "Click here to edit project description.",
                extra_trigger: "#snippet_structure:visible",
                trigger: ".o_web_psc_team_project_description p",
                run: function () {
                    $(".o_web_psc_team_project_description").addClass(
                        "o_dirty"
                    );
                    $(".o_web_psc_team_project_description p").text(
                        "Updated Apps store project description."
                    );
                },
            },

            {
                content: "Click here to save changes.",
                trigger: "button[data-action=save]",
            },

            {
                content: "Go to psc teams page.",
                trigger: "#top_menu li a[href='/psc-teams']",
            },
        ]
    );
});
