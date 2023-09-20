# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleAdvancePaymentOrder(models.TransientModel):
    _name = "sale.make.planned.order"
    _description = "Wizard when create order by plan"

    def create_orders_by_plan(self):
        sale = self.env["sale.blanket.order"].browse(self._context.get("active_id"))
        sale.ensure_one()

        order_plans = (
            self._context.get("all_remain_orders")
            and sale.egd_sale_order_plan_ids.filtered(lambda l: not l.ordered)
            or sale.egd_sale_order_plan_ids.filtered("to_order")
        )

        for plan in order_plans.sorted("installment"):
            sale.with_context(order_plan_id=plan.id)._create_sale_order()
        return {"type": "ir.actions.act_window_close"}
