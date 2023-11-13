# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    egd_target_value = fields.Float(
        string="Target Price Unit", compute="_compute_egd_target_value"
    )

    egd_target_above = fields.Boolean(
        string="Target Above",
        compute="_compute_egd_target_above",
    )

    @api.depends(
        "account_id",
        "unit_amount",
        "amount",
    )
    def _compute_egd_target_value(self):
        for record in self:
            products = False
            services = False
            price_unit = 0
            account_analytic = False
            if record.product_id:
                if record.account_id:
                    account_analytic = record.account_id
                    blanket_orders = record.env["sale.blanket.order"].search(
                        [("analytic_account_id", "=", account_analytic.id)]
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

    @api.depends(
        "account_id",
        "egd_target_value",
        "unit_amount",
        "amount",
    )
    def _compute_egd_target_above(self):
        for record in self:
            target_above = False
            if (record.amount / record.unit_amount) > record.egd_target_value:
                target_above = True
            record.egd_target_above = target_above
