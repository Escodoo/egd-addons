# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseRequestLine(models.Model):

    _inherit = "purchase.request.line"

    estimated_cost = fields.Float(
        compute="_compute_egd_estimated_cost",
        store=True,
        readonly=True,
        tracking=True,
    )

    egd_estimated_unit_cost = fields.Float(
        string="Estimated Unit Cost",
        compute="_compute_egd_estimated_unit_cost",
        readonly=False,
        store=True,
        tracking=True,
    )

    egd_target_value = fields.Float(
        string="Target Unit Price",
        compute="_compute_egd_target_value",
        store=True,
    )

    egd_target_above = fields.Boolean(
        string="Target Above",
        compute="_compute_egd_target_value",
    )

    egd_target_quantity = fields.Float(
        string="Target Quantity",
        compute="_compute_egd_target_quantity",
    )

    egd_product_quantity_requested = fields.Float(
        string="Product Quantity Requested",
        compute="_compute_egd_product_quantity_requested",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        self.invalidate_cache(["egd_product_quantity_requested"])
        return lines

    def write(self, vals):
        result = super().write(vals)
        if {
            "product_qty",
            "product_id",
            "analytic_account_id",
            "request_id",
        } & vals.keys():
            self.invalidate_cache(["egd_product_quantity_requested"])
        return result

    def unlink(self):
        result = super().unlink()
        self.invalidate_cache(["egd_product_quantity_requested"])
        return result

    @api.depends(
        "product_qty",
        "product_id",
        "egd_estimated_unit_cost",
    )
    def _compute_egd_estimated_cost(self):
        """
        Calculate the estimated cost of the purchase request line.
        """
        for line in self:
            line.estimated_cost = line.product_qty * line.egd_estimated_unit_cost

    @api.depends("product_id")
    def _compute_egd_estimated_unit_cost(self):
        for line in self:
            if line.product_id:
                line.egd_estimated_unit_cost = line.product_id.standard_price
            else:
                line.egd_estimated_unit_cost = 0.0

    @api.depends(
        "product_id",
        "analytic_account_id",
        "egd_estimated_unit_cost",
    )
    def _compute_egd_target_value(self):
        for record in self:
            product = False
            service = False
            price_unit = 0
            account_analytic = False
            target_above = False
            if record.product_id:
                if record.analytic_account_id:
                    account_analytic = record.analytic_account_id
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
                        if product.id:
                            price_unit = product.price_unit
                        elif service.id:
                            price_unit = service.price_unit

            record.egd_target_value = price_unit
            if record.egd_estimated_unit_cost > price_unit:
                target_above = True
            record.egd_target_above = target_above

    @api.depends("analytic_account_id", "product_id")
    def _compute_egd_target_quantity(self):
        for record in self:
            target_quantity = 0

            if record.product_id and record.analytic_account_id:
                blanket_orders = record.env["sale.blanket.order"].search(
                    [
                        ("analytic_account_id", "=", record.analytic_account_id.id),
                        ("state", "=", "open"),
                    ],
                )
                product_lines = blanket_orders.mapped("egd_order_product_ids")
                service_lines = blanket_orders.mapped("egd_order_service_ids")

                for line in product_lines:
                    if line.product_id == record.product_id:
                        target_quantity += line.quantity

                for line in service_lines:
                    if line.product_id == record.product_id:
                        target_quantity += line.quantity

            record.egd_target_quantity = target_quantity

    @api.depends(
        "analytic_account_id",
        "product_id",
        "product_qty",
        "request_id.line_ids",
        "request_id.line_ids.product_qty",
        "request_id.line_ids.product_id",
        "request_id.line_ids.analytic_account_id",
    )
    def _compute_egd_product_quantity_requested(self):
        for record in self:
            domain = [
                ("analytic_account_id", "=", record.analytic_account_id.id),
                ("product_id", "=", record.product_id.id),
            ]
            # Replace this request's persisted lines with its form values.
            # This includes new lines and omits lines removed before saving.
            request = record.request_id
            if request._origin:
                domain.append(("request_id", "!=", request._origin.id))
            elif record._origin:
                domain.append(("id", "!=", record._origin.id))
            quantity_requested = sum(record.search(domain).mapped("product_qty"))
            form_lines = request.line_ids if request else record
            # A standalone line form may not share its parent's cached values.
            other_lines = form_lines.filtered(
                lambda line: line != record
                and (not record._origin or line._origin != record._origin)
            )
            for line in other_lines | record:
                if (
                    line.product_id == record.product_id
                    and line.analytic_account_id == record.analytic_account_id
                ):
                    quantity_requested += line.product_qty
            record.egd_product_quantity_requested = quantity_requested
