# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestAccountMovePostAndWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].search(
            [("company_id", "in", [False, cls.env.company.id])],
            limit=1,
        )
        if not cls.analytic_plan:
            cls.analytic_plan = cls.env["account.analytic.plan"].create(
                {
                    "name": "Test Analytic Plan",
                    "company_id": cls.env.company.id,
                }
            )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Customer Test",
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic Test",
                "company_id": cls.env.company.id,
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Stockable Test Product",
                "type": "product",
                "list_price": 100.0,
                "invoice_policy": "order",
            }
        )

    def _create_sale_with_production_date(self, production_date):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "production_date": production_date,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()
        return sale_order

    def test_wizard_default_get_production_date_from_sale(self):
        production_date = fields.Date.to_date("2026-03-18")
        sale_order = self._create_sale_with_production_date(production_date)
        self.assertTrue(sale_order.picking_ids, "Sale order should create a picking.")
        picking = sale_order.picking_ids[0]

        defaults = (
            self.env["stock.invoice.onshipping"]
            .with_context(active_model="stock.picking", active_id=picking.id)
            .default_get(["production_date"])
        )

        self.assertEqual(defaults.get("production_date"), production_date)

    def test_post_updates_analytic_line_date_with_production_date(self):
        production_date = fields.Date.to_date("2026-03-19")
        sale_order = self._create_sale_with_production_date(production_date)
        invoice = sale_order._create_invoices()
        invoice.invoice_date = fields.Date.today()
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda line: not line.display_type
        )[:1]
        self.env["account.analytic.line"].create(
            {
                "name": "Analytic line linked to invoice",
                "account_id": self.analytic_account.id,
                "move_line_id": invoice_line.id,
                "date": fields.Date.to_date("2026-01-01"),
                "amount": -100.0,
            }
        )

        invoice.action_post()

        self.assertEqual(invoice.production_date, production_date)
