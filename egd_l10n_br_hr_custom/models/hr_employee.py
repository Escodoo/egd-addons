# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):

    _inherit = "hr.employee"
    pis_registration_date = fields.Date(
        string="PIS Registration Date",
        help="Date of PIS registration",
        groups="hr.group_hr_user",
    )
