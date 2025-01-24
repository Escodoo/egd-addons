# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    factor_multiplication = fields.Float(
        string="Factor Multiplication (%)",
        default=0.0,
    )
    extra_amount = fields.Monetary(
        string="Extra Amount",
        compute="_compute_extra_amount",
    )

    @api.depends("amount", "factor_multiplication", "unit_amount")
    def _compute_extra_amount(self):
        for record in self:
            cost = record.employee_id.timesheet_cost or 0.0
            base_amount = -record.unit_amount * cost
            record.extra_amount = record.factor_multiplication * base_amount
            record.amount = base_amount + record.extra_amount
