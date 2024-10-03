/* Copyright 2024 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0) */

odoo.define("oca_monetize", function (require) {
    "use strict";

    var core = require("web.core");
    var rpc = require("web.rpc");

    core.bus.on("web_client_ready", null, function () {
        return rpc.query({model: 'oca.monetize', method: 'has_valid_subscription'}).then(function(result) {
            if (result) {
                jQuery("#oca_monetize").remove()
            }
        });
    });

    return {};
});
