# Copyright 2024 - TODAY, Matheus Marques <matheus.marques@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import models


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    def _get_employee_expirations(self):
        expiration_date_threshold = datetime.now() + timedelta(days=30)
        employees = self.env["hr.employee"].search(
            [("expiration_date", "<=", expiration_date_threshold)]
        )
        expirations = []
        for employee in employees:
            days_until_expiration = (
                employee.expiration_date - datetime.now().date()
            ).days
            expirations.append(
                {"name": employee.name, "days_until_expiration": days_until_expiration}
            )
        return expirations

    def action_view_employee_expirations(self):
        expirations = self._get_employee_expirations()
        return {
            "name": "Employees with Expiration Date Approaching",
            "view_mode": "tree",
            "res_model": "employee.expiration",
            "type": "ir.actions.act_window",
            "context": {"create": False},
            "domain": [],
            "view_id": False,
            "views": [(False, "tree")],
            "target": "current",
            "readonly": True,
            "limit": 80,
            "auto_search": False,
            "auto_refresh": 1,
            "expirations": expirations,
        }
