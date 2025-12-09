# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    egd_target_value = fields.Float(
        string="Target Unit Price", compute="_compute_egd_target"
    )

    egd_target_quantity = fields.Float(
        string="Target Quantity", compute="_compute_egd_target"
    )

    egd_target_above = fields.Boolean(
        string="Target Above",
        compute="_compute_egd_target",
    )

    @api.depends(
        "purchase_request_lines",
        "purchase_request_lines.stock_request_ids",
        "purchase_request_lines.stock_request_ids.analytic_distribution",
        "price_unit",
    )
    def _compute_egd_target(self):
        for record in self:
            product = False
            service = False
            price_unit = 0
            account_analytic = False
            target_above = False
            target_quantity = 0
            if record.product_id:
                if record.purchase_request_lines.stock_request_ids:
                    distribution = (
                        record.purchase_request_lines.stock_request_ids[
                            0
                        ].analytic_distribution
                        or {}
                    )
                    account_ids = (
                        list(distribution.keys())
                        if isinstance(distribution, dict)
                        else []
                    )
                    if account_ids:
                        analytic_account = self.env["account.analytic.account"]
                        account_analytic = analytic_account.browse(int(account_ids[0]))
                if account_analytic:
                    blanket_order = record.env["sale.blanket.order"].search(
                        [("analytic_account_id", "=", account_analytic.id)],
                        limit=1,
                        order="id desc",
                    )
                    if blanket_order:
                        product = blanket_order.egd_order_product_ids.search(
                            [
                                ("product_id", "=", record.product_id.id),
                                ("blanket_order_id", "=", blanket_order.id),
                            ],
                            limit=1,
                            order="write_date desc",
                        )
                        service = blanket_order.egd_order_service_ids.search(
                            [
                                ("product_id", "=", record.product_id.id),
                                ("blanket_order_id", "=", blanket_order.id),
                            ],
                            limit=1,
                            order="write_date desc",
                        )
                        if product:
                            price_unit = product.price_unit
                            target_quantity = product.quantity
                        elif service:
                            price_unit = service.price_unit
                            target_quantity = service.quantity

            record.egd_target_value = price_unit
            record.egd_target_quantity = target_quantity
            if record.price_unit > price_unit:
                target_above = True
            record.egd_target_above = target_above
