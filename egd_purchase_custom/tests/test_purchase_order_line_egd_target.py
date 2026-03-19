# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, fields

from odoo.addons.egd_sale_blanket_order_custom.tests.common import (
    EGDSaleBlanketOrderCommon,
)
from odoo.addons.stock_request.tests.test_stock_request import TestStockRequest


class TestPurchaseOrderLineEgdTarget(TestStockRequest, EGDSaleBlanketOrderCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def _prepare_order_request_analytic(self, request_data):
        return {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": fields.Datetime.now(),
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_id": product.uom_id.id,
                        "product_uom_qty": qty,
                        "analytic_distribution": analytic_distribution,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.warehouse.lot_stock_id.id,
                        "expected_date": fields.Datetime.now(),
                    },
                )
                for (product, qty, analytic_distribution) in request_data
            ],
        }

    def _create_required(
        self,
        model_name,
        overrides=None,
        comodel_defaults=None,
        company=None,
    ):
        overrides = overrides or {}
        comodel_defaults = comodel_defaults or {}
        model = self.env[model_name]
        if company:
            model = model.with_company(company).with_context(
                allowed_company_ids=[company.id]
            )
        vals = dict(overrides)
        for fname, field in model._fields.items():
            if fname in vals or not field.required or field.compute:
                continue
            if field.type == "many2one":
                default = comodel_defaults.get(field.comodel_name)
                if default:
                    vals[fname] = default.id
                    continue
                rec = model.env[field.comodel_name].search([], limit=1)
                if rec:
                    vals[fname] = rec.id
                    continue
            elif field.type in ("char", "text"):
                vals[fname] = fname
            elif field.type == "selection":
                selection = field.selection
                if callable(selection):
                    selection = selection(model.env)
                if selection:
                    vals[fname] = selection[0][0]
            elif field.type in ("float", "integer", "monetary"):
                if field.type == "monetary":
                    vals[fname] = 0.0
                else:
                    vals[fname] = 1.0
            elif field.type == "date":
                vals[fname] = fields.Date.today()
            elif field.type == "datetime":
                vals[fname] = fields.Datetime.now()
            elif field.type == "boolean":
                vals[fname] = False
        return model.create(vals)

    def _link_purchase_request_line_to_order_line(self, order_line, stock_request):
        purchase_order_line = self.env["purchase.order.line"]
        pol_field = purchase_order_line._fields["purchase_request_lines"]
        prl_model = pol_field.comodel_name

        purchase_request_company = stock_request.company_id or self.main_company
        if not stock_request.company_id:
            stock_request.with_company(purchase_request_company).with_context(
                allowed_company_ids=[purchase_request_company.id]
            ).write({"company_id": purchase_request_company.id})
        purchase_request = self._create_required(
            "purchase.request",
            overrides={
                "company_id": purchase_request_company.id,
            },
            company=purchase_request_company,
        )

        prl_model = self.env[prl_model]

        inverse_name = (
            pol_field.inverse_name
            if pol_field.type == "one2many" and pol_field.inverse_name
            else False
        )
        prl_overrides = {}
        if "purchase_request_id" in prl_model._fields:
            prl_overrides["purchase_request_id"] = purchase_request.id
        if "request_id" in prl_model._fields:
            prl_overrides["request_id"] = purchase_request.id
        if "product_id" in prl_model._fields:
            prl_overrides["product_id"] = order_line.product_id.id
        if "company_id" in prl_model._fields:
            prl_overrides["company_id"] = purchase_request_company.id
        if inverse_name:
            prl_overrides[inverse_name] = order_line.id

        # Fill required many2one/uom fields if they exist.
        comodel_defaults = {
            "res.partner": self.env.ref("base.res_partner_3"),
            "product.product": order_line.product_id,
            "uom.uom": order_line.product_uom,
            "purchase.request": purchase_request,
            "stock.request": stock_request,
            "res.company": purchase_request_company,
        }
        prl = self._create_required(
            prl_model._name,
            overrides=prl_overrides,
            comodel_defaults=comodel_defaults,
            company=purchase_request_company,
        )
        if (
            "company_id" in prl_model._fields
            and not prl_model._fields["company_id"].related
            and prl.company_id != purchase_request_company
        ):
            prl.with_company(purchase_request_company).with_context(
                allowed_company_ids=[purchase_request_company.id]
            ).write({"company_id": purchase_request_company.id})
        if "request_id" in prl_model._fields and prl.request_id != purchase_request:
            prl.with_company(purchase_request_company).with_context(
                allowed_company_ids=[purchase_request_company.id]
            ).write({"request_id": purchase_request.id})

        stock_request_link_vals = {}
        if "stock_request_ids" in prl_model._fields:
            stock_request_link_vals["stock_request_ids"] = [
                Command.set(stock_request.ids)
            ]
        elif "stock_request_id" in prl_model._fields:
            stock_request_link_vals["stock_request_id"] = stock_request.id
        if stock_request_link_vals:
            prl.with_company(purchase_request_company).with_context(
                allowed_company_ids=[purchase_request_company.id]
            ).write(stock_request_link_vals)

        if not inverse_name:
            order_line.write({"purchase_request_lines": [Command.link(prl.id)]})
        return prl

    def test_egd_target_from_blanket_product_cost(self):
        self.assertTrue(self.blanket)
        analytic_distribution = {str(self.analytic_account_a1.id): 100.0}
        stock_request_order = self.request_order.with_company(self.main_company).create(
            self._prepare_order_request_analytic(
                [(self.product_a, 5.0, analytic_distribution)]
            )
        )
        stock_request = stock_request_order.stock_request_ids[0]

        product_cost = self.env["egd.sale.blanket.order.product"].create(
            {
                "blanket_order_id": self.blanket.id,
                "product_id": self.product_a.id,
                "quantity": 7.0,
                "price_unit": 40.0,
            }
        )
        self.assertTrue(product_cost)

        purchase_order_company = stock_request.company_id or self.main_company
        purchase_order = self._create_required(
            "purchase.order",
            overrides={
                "partner_id": self.partner_a.id,
                "company_id": purchase_order_company.id,
                "currency_id": purchase_order_company.currency_id.id,
            },
            company=purchase_order_company,
        )
        order_line = self._create_required(
            "purchase.order.line",
            overrides={
                "order_id": purchase_order.id,
                "product_id": self.product_a.id,
                "name": self.product_a.display_name,
                "product_qty": 1.0,
                "price_unit": 50.0,
                "product_uom": self.product_a.uom_id.id,
            },
            company=purchase_order_company,
        )

        self._link_purchase_request_line_to_order_line(order_line, stock_request)

        order_line._compute_egd_target()
        self.assertEqual(order_line.egd_target_value, 40.0)
        self.assertEqual(order_line.egd_target_quantity, 7.0)
        self.assertTrue(order_line.egd_target_above)

    def test_egd_target_from_blanket_service_cost(self):
        analytic_distribution = {str(self.analytic_account_a1.id): 100.0}
        stock_request_order = self.request_order.with_company(self.main_company).create(
            self._prepare_order_request_analytic(
                [(self.service_a, 3.0, analytic_distribution)]
            )
        )
        stock_request = stock_request_order.stock_request_ids[0]

        self.env["egd.sale.blanket.order.product"].search(
            [
                ("blanket_order_id", "=", self.blanket.id),
                ("product_id", "=", self.service_a.id),
            ]
        ).unlink()

        service_cost = self.env["egd.sale.blanket.order.service"].create(
            {
                "blanket_order_id": self.blanket.id,
                "product_id": self.service_a.id,
                "quantity": 9.0,
                "price_unit": 80.0,
            }
        )
        self.assertTrue(service_cost)

        purchase_order_company = stock_request.company_id or self.main_company
        purchase_order = self._create_required(
            "purchase.order",
            overrides={
                "partner_id": self.partner_a.id,
                "company_id": purchase_order_company.id,
                "currency_id": purchase_order_company.currency_id.id,
            },
            company=purchase_order_company,
        )
        order_line = self._create_required(
            "purchase.order.line",
            overrides={
                "order_id": purchase_order.id,
                "product_id": self.service_a.id,
                "name": self.service_a.display_name,
                "product_qty": 1.0,
                "price_unit": 100.0,
                "product_uom": self.service_a.uom_id.id,
            },
            company=purchase_order_company,
        )

        self._link_purchase_request_line_to_order_line(order_line, stock_request)
        order_line._compute_egd_target()
        self.assertEqual(order_line.egd_target_value, 80.0)
        self.assertEqual(order_line.egd_target_quantity, 9.0)
        self.assertTrue(order_line.egd_target_above)

    def test_egd_target_without_stock_request_link(self):
        purchase_order = self._create_required(
            "purchase.order",
            overrides={
                "partner_id": self.partner_a.id,
                "company_id": self.main_company.id,
                "currency_id": self.main_company.currency_id.id,
            },
            company=self.main_company,
        )
        order_line = self._create_required(
            "purchase.order.line",
            overrides={
                "order_id": purchase_order.id,
                "product_id": self.product_a.id,
                "name": self.product_a.display_name,
                "product_qty": 1.0,
                "price_unit": 50.0,
                "product_uom": self.product_a.uom_id.id,
            },
            company=self.main_company,
        )
        order_line._compute_egd_target()
        self.assertEqual(order_line.egd_target_value, 0.0)
        self.assertEqual(order_line.egd_target_quantity, 0.0)
        self.assertTrue(order_line.egd_target_above)

    def test_egd_target_not_above_when_price_equals_target(self):
        analytic_distribution = {str(self.analytic_account_a1.id): 100.0}
        stock_request_order = self.request_order.with_company(self.main_company).create(
            self._prepare_order_request_analytic(
                [(self.product_a, 2.0, analytic_distribution)]
            )
        )
        stock_request = stock_request_order.stock_request_ids[0]
        self.env["egd.sale.blanket.order.product"].create(
            {
                "blanket_order_id": self.blanket.id,
                "product_id": self.product_a.id,
                "quantity": 2.0,
                "price_unit": 50.0,
            }
        )
        purchase_order_company = stock_request.company_id or self.main_company
        purchase_order = self._create_required(
            "purchase.order",
            overrides={
                "partner_id": self.partner_a.id,
                "company_id": purchase_order_company.id,
                "currency_id": purchase_order_company.currency_id.id,
            },
            company=purchase_order_company,
        )
        order_line = self._create_required(
            "purchase.order.line",
            overrides={
                "order_id": purchase_order.id,
                "product_id": self.product_a.id,
                "name": self.product_a.display_name,
                "product_qty": 1.0,
                "price_unit": 50.0,
                "product_uom": self.product_a.uom_id.id,
            },
            company=purchase_order_company,
        )
        self._link_purchase_request_line_to_order_line(order_line, stock_request)
        order_line._compute_egd_target()
        self.assertEqual(order_line.egd_target_value, 50.0)
        self.assertEqual(order_line.egd_target_quantity, 2.0)
        self.assertFalse(order_line.egd_target_above)
