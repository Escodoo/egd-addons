# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = "stock.invoice.onshipping"

    production_date = fields.Date(string="Production Date")

    def _action_generate_invoices(self):
        invoices = super()._action_generate_invoices()

        for invoice in invoices:
            if invoice.invoice_line_ids:
                invoice.write({"production_date": self.production_date})

        return invoices
