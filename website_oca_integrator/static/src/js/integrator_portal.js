/* Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define("website_oca_integrator.website_oca_integrator", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");

    publicWidget.registry.integratorModuleSelector = publicWidget.Widget.extend({
        selector: "input.module_js_select2",

        /**
         * @override
         */
        start: function () {
            this.$el.select2({
                tags: true,
                maximumInputLength: 25,
                maximumSelectionSize: 5,
                ajax: {
                    url: "/my/account/get_developed_modules",
                    dataType: "json",
                    data: (term) => {
                        return {query: term, limit: 25};
                    },
                    results: (data) => {
                        const res = [];
                        _.each(data, (x) => {
                            res.push({id: x.id, text: x.name});
                        });
                        return {results: res};
                    },
                },
                initSelection: (element, callback) =>
                    $.ajax({
                        type: "GET",
                        url: "/my/account/get_favourite_modules",
                        dataType: "json",
                        success: (data) => {
                            const res = [];
                            _.each(data, (x) => {
                                res.push({id: x.id, text: x.name});
                            });
                            element.val("");
                            callback(res);
                        },
                    }),
            });
        },
    });

    publicWidget.registry.integratorDescriptionEditor = publicWidget.Widget.extend({
        selector: "textarea.website_description_editor",
        events: {"click button, .a-submit": "_submit"},
        assetLibs: ["web_editor.compiled_assets_wysiwyg"],

        /**
         * @override
         */
        start: function () {
            if (!this.$el.val().match(/\S/)) {
                this.$el.val("<p><br/></p>");
            }
            const toolbar = [
                ["style", ["style"]],
                ["font", ["bold", "italic", "underline", "clear"]],
                ["para", ["ul", "ol", "paragraph"]],
                ["table", ["table"]],
                ["history", ["undo", "redo"]],
            ];
            this.$el.summernote({
                height: 200,
                toolbar: toolbar,
                styleWithSpan: false,
            });
        },
        _submit: function () {
            const $form = this.$el.closest("form");
            this.$el.html($form.find(".note-editable").code());
        },
    });
});
