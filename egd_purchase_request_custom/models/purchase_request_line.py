# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseRequestLine(models.Model):

    _inherit = "purchase.request.line"

    estimated_cost = fields.Float(
        compute="_compute_egd_estimated_cost", store=True, tracking=True
    )

    egd_estimated_unit_cost = fields.Float(
        string="Estimated Unit Cost",
        compute="_compute_egd_estimated_unit_cost",
        readonly=False,
        store=True,
        tracking=True,
    )

    egd_target_value = fields.Float(
        string="Target Unit Price", compute="_compute_egd_target_value"
    )

    egd_target_above = fields.Boolean(
        string="Target Above",
        compute="_compute_egd_target_above",
    )

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
        """
        Compute the estimated unit cost based on product's standard price.
        """
        for line in self:
            if line.product_id:
                line.egd_estimated_unit_cost = line.product_id.standard_price
            else:
                line.egd_estimated_unit_cost = 0.0

    @api.depends(
        "analytic_account_id",
        "egd_estimated_unit_cost",
    )
    def _compute_egd_target_value(self):
        for record in self:
            product = False
            service = False
            price_unit = 0
            account_analytic = False
            if record.product_id:
                if record.analytic_account_id:
                    account_analytic = record.analytic_account_id
                if account_analytic:
                    purchase_requests = record.env["purchase.request.line"].search(
                        [("analytic_account_id", "=", account_analytic.id)]
                    )
                    if purchase_requests:
                        product = record.env["product.product"].search(
                            [("id", "=", record.product_id.id)],
                            limit=1,
                            order="write_date desc",
                        )
                        service = record.env["product.product"].search(
                            [("id", "=", record.product_id.id)],
                            limit=1,
                            order="write_date desc",
                        )
                        if product:
                            price_unit = product.standard_price
                        elif service:
                            price_unit = service.standard_price
            record.egd_target_value = price_unit

    @api.depends(
        "analytic_account_id",
        "egd_target_value",
        "egd_estimated_unit_cost",
    )
    def _compute_egd_target_above(self):
        for record in self:
            target_above = False
            if record.egd_estimated_unit_cost > record.egd_target_value:
                target_above = True
            record.egd_target_above = target_above
