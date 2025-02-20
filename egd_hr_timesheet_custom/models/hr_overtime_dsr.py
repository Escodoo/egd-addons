# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrOvertimeDsr(models.Model):
    _name = "hr.overtime.dsr"
    _description = "DSR Calculation for Overtime"
    _order = "year desc, month desc"

    month = fields.Char(
        "Month",
        size=2,
        required=True,
        default=lambda r: str(datetime.date.today().month),
    )
    year = fields.Char(
        "Year", size=4, required=True, default=lambda r: str(datetime.date.today().year)
    )
    working_days = fields.Integer(
        string="Working Days",
        required=True,
    )
    dsr_count = fields.Integer(
        string="DSR Count",
        required=True,
    )

    @api.constrains("month", "year")
    def _check_unique_month_year(self):
        for record in self:
            existing = self.search(
                [
                    ("month", "=", record.month),
                    ("year", "=", record.year),
                    ("id", "!=", record.id),
                ]
            )
            if existing:
                raise ValidationError(
                    _("A record with the same Month and Year already exists.")
                )

    @api.constrains("working_days", "dsr_count")
    def _check_positive_values(self):
        """Ensure that working days and DSR count are positive values."""
        for record in self:
            if record.working_days < 1 or record.dsr_count < 1:
                raise ValidationError(
                    _("Working days and DSR count must be at least 1.")
                )
