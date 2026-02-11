/** @odoo-module **/

/* Copyright 2018-2026 Surekha Technologies, Therp Bv
License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import publicWidget from "@web/legacy/js/public/public_widget";

function hasPlugin($el, name) {
    return Boolean($el && typeof $el[name] === "function");
}

publicWidget.registry.integratorModuleSelector = publicWidget.Widget.extend({
    selector: ".module_js_select2",

    async start() {
        // Odoo 18: do NOT call this._super() here (it's not available).
        // Keep code resilient to missing jQuery plugins.

        try {
            if (hasPlugin(this.$el, "select2")) {
                this.$el.select2({
                    tags: false,
                    maximumInputLength: 25,
                    maximumSelectionLength: 5,
                    ajax: {
                        url: "/my/account/get_developed_modules",
                        dataType: "json",
                        data: (params) => ({query: params.term, limit: 25}),
                        processResults: (data) => ({
                            results: data.map((x) => ({id: x.id, text: x.name})),
                        }),
                    },
                });
            }
        } catch {
            // Fallback: plain <select multiple>
        }

        // Always populate favourites (works with or without select2).
        const data = await $.ajax({
            type: "GET",
            url: "/my/account/get_favourite_modules",
            dataType: "json",
        });

        const options = data.map((x) => new Option(x.name, x.id, true, true));
        this.$el.append(options).trigger("change");
    },
});

publicWidget.registry.integratorDescriptionEditor = publicWidget.Widget.extend({
    selector: "textarea.website_description_editor",
    events: {
        "click button, click .a-submit": "_submit",
    },

    start() {
        // Odoo 18: do NOT call this._super() here.

        if (!this.$el.val().match(/\S/)) {
            this.$el.val("");
        }

        try {
            if (hasPlugin(this.$el, "summernote")) {
                this.$el.summernote({
                    height: 200,
                    toolbar: [
                        ["style", ["style"]],
                        ["font", ["bold", "italic", "underline", "clear"]],
                        ["para", ["ul", "ol", "paragraph"]],
                        ["table", ["table"]],
                        ["history", ["undo", "redo"]],
                    ],
                    styleWithSpan: false,
                });
            }
        } catch {
            // Fallback: plain textarea
        }
    },

    _submit() {
        try {
            if (hasPlugin(this.$el, "summernote")) {
                this.$el.val(this.$el.summernote("code"));
            }
        } catch {
            // Keep textarea content
        }
    },
});
