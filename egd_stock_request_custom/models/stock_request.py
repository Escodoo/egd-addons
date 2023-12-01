# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRequest(models.Model):

    _inherit = "stock.request"

    egd_target_value = fields.Float(
        string="Target Price Unit", compute="_compute_egd_target_value"
    )

    egd_target_above = fields.Boolean(
        string="Target Above",
        compute="_compute_egd_target_above",
    )

    egd_standard_price = fields.Float(
        string="Standard Price",
        related="product_id.standard_price",
    )

    @api.depends("analytic_account_id")
    def _compute_egd_target_value(self):
        for record in self:
            products = False
            services = False
            price_unit = 0
            if record.product_id and record.analytic_account_id:
                blanket_orders = record.env["sale.blanket.order"].search(
                    [("analytic_account_id", "=", record.analytic_account_id.id)]
                )
                if blanket_orders:
                    products = blanket_orders.egd_order_product_ids.search(
                        [("product_id", "=", record.product_id.id)]
                    )
                    services = blanket_orders.egd_order_service_ids.search(
                        [("product_id", "=", record.product_id.id)]
                    )
                    if products:
                        price_unit = products[0].price_unit
                    elif services:
                        price_unit = services[0].price_unit
            record.egd_target_value = price_unit

    @api.depends("analytic_account_id", "egd_target_value", "egd_standard_price")
    def _compute_egd_target_above(self):
        for record in self:
            target_above = False
            if record.egd_standard_price > record.egd_target_value:
                target_above = True
            record.egd_target_above = target_above
