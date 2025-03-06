# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    overtime_factor_id = fields.Many2one(
        "hr.overtime.factor",
        string="Overtime",
    )
    overtime_dsr_id = fields.Many2one(
        "hr.overtime.dsr",
        string="Overtime DSR",
    )

    overtime_rate = fields.Float(
        string="Overtime Rate",
        related="overtime_factor_id.rate",
        readonly=True,
    )
    overtime_dsr_factor = fields.Float(
        string="DSR Factor",
        readonly=True,
    )

    extra_amount = fields.Monetary(
        string="Extra Amount",
        readonly=True,
    )

    @api.onchange("unit_amount", "date", "overtime_factor_id")
    def _onchange_overtime_dsr(self):
        for record in self:
            if record.date and record.overtime_factor_id:
                month = record.date.month
                year = record.date.year

                overtime_dsr = self.env["hr.overtime.dsr"].search(
                    [("month", "=", month), ("year", "=", year)], limit=1
                )
                record.overtime_dsr_id = overtime_dsr.id if overtime_dsr else False

    def _timesheet_postprocess_values(self, values):
        result = super()._timesheet_postprocess_values(values)

        sudo_self = self.sudo()
        if any(
            field_name in values
            for field_name in [
                "unit_amount",
                "employee_id",
                "account_id",
                "overtime_rate",
                "overtime_dsr_id",
            ]
        ):
            for timesheet in sudo_self:
                extra_amount = 0.0
                overtime_dsr_factor = 0.0
                total_amount = result[timesheet.id].get("amount", 0.0)

                if timesheet.employee_id and timesheet.overtime_factor_id:
                    cost_overtime = timesheet.employee_id.timesheet_cost_overtime or 0.0
                    extra_amount = (
                        -timesheet.unit_amount * cost_overtime * timesheet.overtime_rate
                    )

                    if (
                        timesheet.overtime_dsr_id
                        and timesheet.overtime_dsr_id.working_days > 0
                    ):
                        overtime_dsr_factor = (
                            extra_amount
                            / timesheet.overtime_dsr_id.working_days
                            * timesheet.overtime_dsr_id.dsr_count
                        )

                    total_amount = extra_amount + overtime_dsr_factor

                result[timesheet.id].update(
                    {
                        "amount": timesheet.employee_id.currency_id._convert(
                            total_amount,
                            timesheet.account_id.currency_id or timesheet.currency_id,
                            self.env.company,
                            timesheet.date,
                        ),
                        "extra_amount": extra_amount,
                        "overtime_dsr_factor": overtime_dsr_factor,
                    }
                )

        return result
