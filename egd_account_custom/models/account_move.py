# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    egd_invoice_due_date = fields.Date(
        related="invoice_date_due",
        string="Full Date Format (Due Date)",
        store=True,
        readonly=True,
    )

    @api.depends("move_type")
    def _compute_invoice_default_sale_person(self):
        res = super()._compute_invoice_default_sale_person()
        for move in self:
            if not move.is_sale_document(include_receipts=True):
                move.invoice_user_id = move.invoice_user_id or self.env.user
        return res
