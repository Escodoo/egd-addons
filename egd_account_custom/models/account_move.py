# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    egd_invoice_due_date = fields.Date(
        related="invoice_date_due",
        string="Full Date Format (Due Date)",
        store=True,
        readonly=True,
    )
