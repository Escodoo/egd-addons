# Copyright 2024 - TODAY Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    timesheet_cost = fields.Monetary(
        tracking=True,
    )
