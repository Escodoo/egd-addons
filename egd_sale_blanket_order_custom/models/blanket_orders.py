# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round


class SaleBlanketOrder(models.Model):
    _inherit = "sale.blanket.order"

    order_plan_ids = fields.One2many(
        comodel_name="sale.order.plan",
        inverse_name="sale_id",
        string="Order Plan",
        copy=False,
    )
    use_order_plan = fields.Boolean(
        string="Use Order Plan",
        default=False,
        copy=False,
    )
    ip_order_plan = fields.Boolean(
        string="Order Plan In Process",
        compute="_compute_ip_order_plan",
        help="At least one order plan line pending to create order",
    )
    egd_order_product = fields.One2many(
        "egd.sale.blanket.order.product",
        "blanket_order_id",
        string="Blanket Order Products",
    )

    egd_order_service = fields.One2many(
        "egd.sale.blanket.order.service",
        "blanket_order_id",
        string="Blanket Order Services",
    )

    egd_product_total = fields.Monetary(
        "egd_order_product.amount_total", compute="_compute_egd_total_order_product"
    )

    egd_service_total = fields.Monetary(
        "egd_order_service.amount_total", compute="_compute_egd_total_order_service"
    )

    egd_profit = fields.Monetary(
        string="Profit", compute="_compute_egd_profit", store=True
    )

    def _compute_ip_order_plan(self):
        for rec in self:
            has_order_plan = rec.use_order_plan and rec.order_plan_ids
            to_order = rec.order_plan_ids.filtered(lambda l: not l.ordered)
            if rec.state == "open" and has_order_plan and to_order:
                rec.ip_order_plan = True
                continue
            rec.ip_order_plan = False

    @api.constrains("state")
    def _check_order_plan(self):
        for rec in self:
            if rec.state != "draft":
                if rec.order_plan_ids.filtered(lambda l: not l.percent):
                    raise ValidationError(
                        _("Please fill percentage for all order plan lines")
                    )

    def action_confirm(self):
        if self.filtered(lambda r: r.use_order_plan and not r.order_plan_ids):
            raise UserError(_("Use Order Plan selected, but no plan created"))
        return super().action_confirm()

    def create_order_plan(
        self, num_installment, installment_date, interval, interval_type
    ):
        self.ensure_one()
        self.order_plan_ids.unlink()
        order_plans = []
        Decimal = self.env["decimal.precision"]
        prec = Decimal.precision_get("Product Unit of Measure")
        percent = float_round(1.0 / num_installment * 100, prec)
        percent_last = 100 - (percent * (num_installment - 1))
        # Normal
        for i in range(num_installment):
            this_installment = i + 1
            if num_installment == this_installment:
                percent = percent_last
            vals = {
                "installment": this_installment,
                "plan_date": installment_date,
                "order_type": "installment",
                "percent": percent,
            }
            order_plans.append((0, 0, vals))
            installment_date = self._next_date(
                installment_date, interval, interval_type
            )
        self.write({"order_plan_ids": order_plans})
        return True

    def remove_order_plan(self):
        self.ensure_one()
        self.order_plan_ids.unlink()
        return True

    @api.model
    def _next_date(self, installment_date, interval, interval_type):
        installment_date = fields.Date.from_string(installment_date)
        if interval_type == "month":
            next_date = installment_date + relativedelta(months=+interval)
        elif interval_type == "year":
            next_date = installment_date + relativedelta(years=+interval)
        else:
            next_date = installment_date + relativedelta(days=+interval)
        next_date = fields.Date.to_string(next_date)
        return next_date

    def _create_sale_order(self):
        order_plan_id = self._context.get("order_plan_id")
        lines = [
            (
                0,
                0,
                {
                    "blanket_line_id": line.id,
                    "product_id": line.product_id.id,
                    "date_schedule": line.date_schedule,
                    "remaining_uom_qty": line.remaining_uom_qty,
                    "price_unit": line.price_unit,
                    "product_uom": line.product_uom,
                    "qty": line.remaining_uom_qty,
                    "partner_id": line.partner_id,
                },
            )
            for line in self.line_ids
        ]

        wizard = (
            self.env["sale.blanket.order.wizard"]
            .with_context(active_id=self.id, active_model="sale.blanket.order")
            .create({"blanket_order_id": self.id, "line_ids": lines})
        )

        result = wizard.create_sale_order()  # Create Sale Order using Wizard
        sale_order_id = result.get("domain", [])[0][2][0]  # Get ID in domain
        orders = self.env["sale.order"].search(
            [("id", "=", sale_order_id)]
        )  # Easy locate for sale.order
        blanket_orders = self.env["sale.blanket.order"].browse(
            self.id
        )  # Usage for compute new quantity
        if order_plan_id:
            plan = self.env["sale.order.plan"].browse(order_plan_id)
            for order in orders:
                plan._compute_new_order_quantity(blanket_orders)
                order.date_order = plan.plan_date
            plan.sale_order_ids += orders
        return orders

    @api.depends("egd_order_product.amount_total", "egd_order_service.amount_total")
    def _compute_egd_profit(self):
        for order in self:
            order.egd_profit = sum(
                [line.amount_total for line in order.egd_order_product]
            ) + sum([line.amount_total for line in order.egd_order_service])

    def _compute_egd_total_order_product(self):
        for order in self:
            order.egd_product_total = sum(
                [line.amount_total for line in order.egd_order_product]
            )

    def _compute_egd_total_order_service(self):
        for order in self:
            order.egd_service_total = sum(
                [line.amount_total for line in order.egd_order_service]
            )

    @api.onchange("egd_order_product", "egd_order_service")
    def _onchange_egd_order_product_service(self):
        for order in self:
            order.egd_service_total = sum(
                [line.amount_total for line in order.egd_order_service]
            )
            order.egd_product_total = sum(
                [line.amount_total for line in order.egd_order_product]
            )
