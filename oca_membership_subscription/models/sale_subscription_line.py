# Copyright 2026 Akretion (https://www.akretion.com).
# @author Benoit GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class SaleSubscriptionLine(models.Model):
    _inherit = "sale.subscription.line"

    partner_id = fields.Many2one(comodel_name="res.partner", string="Delegated member")

    def _prepare_account_move_line(self):
        vals = super()._prepare_account_move_line()
        start_date = self.sale_subscription_id.recurring_next_date
        vals["start_date"] = start_date
        type_interval = self.sale_subscription_id.template_id.recurring_rule_type
        interval = int(self.sale_subscription_id.template_id.recurring_interval)
        end_date = start_date + relativedelta(**{type_interval: interval})
        vals["end_date"] = end_date
        vals["delegated_member_id"] = self.partner_id.id
        return vals
