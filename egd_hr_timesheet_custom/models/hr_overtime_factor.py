# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrOvertimeFactor(models.Model):
    _name = "hr.overtime.factor"

    name = fields.Char(required=True)
    rate = fields.Float(string="Percentage (%)", default=0.0, required=True)
