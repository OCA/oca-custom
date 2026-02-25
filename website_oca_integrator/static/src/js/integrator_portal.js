/** @odoo-module **/

/* Copyright 2018-2026 Surekha Technologies, Therp Bv
License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import publicWidget from "@web/legacy/js/public/public_widget";

function hasPlugin($el, name) {
    return Boolean($el && typeof $el[name] === "function");
}

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
