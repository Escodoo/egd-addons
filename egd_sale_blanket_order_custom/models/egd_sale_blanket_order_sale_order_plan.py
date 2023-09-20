# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round


class EgdSaleBlanketOrderSaleOrderPlan(models.Model):
    _name = "egd.sale.blanket.order.sale.order.plan"
    _description = "Sale Order Planning Detail"
    _order = "installment"

    sale_id = fields.Many2one(
        comodel_name="sale.blanket.order",
        string="Sales Order",
        index=True,
        readonly=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        related="sale_id.partner_id",
        store=True,
        index=True,
    )
    state = fields.Selection(
        string="Status",
        related="sale_id.state",
        store=True,
        index=True,
    )
    installment = fields.Integer(string="Installment")
    plan_date = fields.Date(string="Plan Date", required=True)
    order_type = fields.Selection(
        [("installment", "Installment")],
        string="Type",
        required=True,
        default="installment",
    )
    last = fields.Boolean(
        string="Last Installment",
        compute="_compute_last",
        help="Last installment will create order use remaining amount",
    )
    percent = fields.Float(
        string="Percent",
        digits="Product Unit of Measure",
        help="This percent will be used to calculate new quantity",
    )
    sale_order_ids = fields.Many2many(
        "sale.order",
        relation="sale_order_plan_order_rel",
        column1="plan_id",
        column2="order_id",
        string="Orders",
        readonly=True,
    )
    to_order = fields.Boolean(
        string="Next Order",
        compute="_compute_to_order",
        help="If this line is ready to create new order",
    )
    ordered = fields.Boolean(
        string="Order Created",
        compute="_compute_ordered",
        help="If this line already ordered",
    )
    _sql_constraint = [
        (
            "unique_instalment",
            "UNIQUE (sale_id, installment)",
            "Installment must be unique on order plan",
        )
    ]

    def _compute_to_order(self):
        """If any order is in draft/done do not allow to create sale order.
        Only if previous to_order is False, it is eligible to_order.
        """
        for rec in self:
            rec.to_order = False
        for rec in self.sorted("installment"):
            if rec.state != "open":  # Not confirmed, no to_order
                continue
            if not rec.ordered:
                rec.to_order = True
                break

    def _compute_ordered(self):
        for rec in self:
            ordered = rec.sale_order_ids.filtered(
                lambda l: l.state in ("draft", "sale")
            )
            rec.ordered = ordered and True or False

    def _compute_last(self):
        for rec in self:
            last = max(rec.sale_id.egd_sale_order_plan_ids.mapped("installment"))
            rec.last = rec.installment == last

    def _compute_new_order_quantity(self, blanket_order):
        self.ensure_one()
        if self.last:  # For last install, let the system do the calc.
            return
        percent = self.percent
        for blanket_line in blanket_order.line_ids:
            first_blanket = fields.first(blanket_line)
            plan_qty = first_blanket.original_uom_qty * (percent / 100)
            prec = first_blanket.product_uom.rounding
            for order_line in blanket_line.sale_lines:
                if not len(order_line):
                    raise UserError(_("No matched order line for sale order"))
                if plan_qty:
                    plan_qty = float_round(plan_qty, precision_rounding=prec)
                if float_compare(plan_qty, order_line.product_uom_qty, prec) == 1:
                    raise ValidationError(
                        _(
                            "Plan quantity: %s, exceeds orderable quantity: %s"
                            "\nProduct should be available before creating the order"
                        )
                        % (plan_qty, order_line.product_uom_qty)
                    )
                order_line.write({"product_uom_qty": plan_qty})
