/* Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define("website_oca_integrator.website_oca_integrator", function(require) {
    "use strict";

    require("web.dom_ready");

    $("input.module_js_select2").select2({
        tags: true,
        maximumInputLength: 25,
        maximumSelectionSize: 5,
        ajax: {
            url: "/my/account/get_developed_modules",
            dataType: "json",
            data: function(term) {
                return {
                    query: term,
                    limit: 25,
                };
            },
            results: function(data) {
                var res = [];
                _.each(data, function(x) {
                    res.push({id: x.id, text: x.name});
                });
                return {results: res};
            },
        },
        initSelection: function(element, callback) {
            return $.ajax({
                type: "GET",
                url: "/my/account/get_favourite_modules",
                dataType: "json",
                success: function(data) {
                    var res = [];
                    _.each(data, function(x) {
                        res.push({id: x.id, text: x.name});
                    });
                    element.val("");
                    callback(res);
                },
            });
        },
    });

    $("textarea.website_description_editor").each(function() {
        var $textarea = $(this);
        if (!$textarea.val().match(/\S/)) {
            $textarea.val("<p><br/></p>");
        }
        var $form = $textarea.closest("form");
        var toolbar = [
            ["style", ["style"]],
            ["font", ["bold", "italic", "underline", "clear"]],
            ["para", ["ul", "ol", "paragraph"]],
            ["table", ["table"]],
            ["history", ["undo", "redo"]],
        ];
        $textarea.summernote({
            height: 200,
            toolbar: toolbar,
            styleWithSpan: false,
        });
        $form.on("click", "button, .a-submit", function() {
            $textarea.html($form.find(".note-editable").code());
        });
    });
});
