# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = "stock.invoice.onshipping"

    production_date = fields.Date(string="Production Date", required=True)

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if self.env.context.get("active_model") == "stock.picking":
            picking_id = self.env.context.get("active_id")
            if picking_id:
                picking = self.env["stock.picking"].browse(picking_id)
                if picking.sale_id and picking.sale_id.production_date:
                    defaults["production_date"] = picking.sale_id.production_date
        return defaults
