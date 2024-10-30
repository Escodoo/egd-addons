# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    production_date = fields.Date(string="Production Date")

    def _create_invoices(self, grouped=False, final=False):
        invoices = super()._create_invoices(grouped=grouped, final=final)
        for invoice in invoices:
            invoice.production_date = self.production_date
        return invoices
