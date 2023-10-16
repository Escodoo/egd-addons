# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeMedicalExamination(models.Model):

    _inherit = "hr.employee.medical.examination"

    egd_expiration_date = fields.Date(string="Expiration Date")
