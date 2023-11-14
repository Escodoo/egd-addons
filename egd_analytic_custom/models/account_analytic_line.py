# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    egd_target_value = fields.Float(
        string="Target Unit Price", compute="_compute_egd_target_value"
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
            product = False
            service = False
            price_unit = 0
            account_analytic = False
            if record.product_id and record.amount < 0:
                if record.account_id:
                    account_analytic = record.account_id
                    blanket_orders = record.env["sale.blanket.order"].search(
                        [("analytic_account_id", "=", account_analytic.id)]
                    )
                    if blanket_orders:
                        product = blanket_orders.egd_order_product_ids.search(
                            [("product_id", "=", record.product_id.id)],
                            limit=1,
                            order="write_date desc",
                        )
                        service = blanket_orders.egd_order_service_ids.search(
                            [("product_id", "=", record.product_id.id)],
                            limit=1,
                            order="write_date desc",
                        )
                        if product:
                            price_unit = product.price_unit
                        elif service:
                            price_unit = service.price_unit
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
            if record.amount and record.unit_amount and record.egd_target_value:
                if (
                    abs(record.amount) / abs(record.unit_amount)
                ) > record.egd_target_value:
                    target_above = True
            record.egd_target_above = target_above
