# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountAnalyticLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env.company
        cls.partner = cls.env["res.partner"].create({"name": "Partner Test"})
        AnalyticPlan = cls.env["account.analytic.plan"]
        cls.analytic_plan = AnalyticPlan.search(
            [("company_id", "=", cls.Company.id)], limit=1
        )
        if not cls.analytic_plan:
            cls.analytic_plan = AnalyticPlan.create(
                {
                    "name": "Analytic Plan Test",
                    "company_id": cls.Company.id,
                }
            )

        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic Test",
                "company_id": cls.Company.id,
                "plan_id": cls.analytic_plan.id,
            }
        )
        Pricelist = cls.env["product.pricelist"]
        cls.pricelist = Pricelist.search([("company_id", "=", cls.Company.id)], limit=1)
        if not cls.pricelist:
            cls.pricelist = Pricelist.create(
                {
                    "name": "Test Pricelist",
                    "currency_id": cls.Company.currency_id.id,
                    "company_id": cls.Company.id,
                }
            )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "service",
            }
        )
        cls.blanket_order = cls.env["sale.blanket.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.product_line = cls.blanket_order.egd_order_product_ids.create(
            {
                "blanket_order_id": cls.blanket_order.id,
                "product_id": cls.product.id,
                "price_unit": 100.0,
            }
        )

    def _create_analytic_line(self, amount, unit_amount=1.0, product=None):
        return self.env["account.analytic.line"].create(
            {
                "name": "Analytic Line Test",
                "account_id": self.analytic_account.id,
                "product_id": (product or self.product).id,
                "unit_amount": unit_amount,
                "amount": amount,
            }
        )

    def test_egd_target_value_from_product_line(self):
        line = self._create_analytic_line(amount=-200.0, unit_amount=2.0)
        self.assertEqual(line.egd_target_value, 100.0)

    def test_egd_target_above_true_when_amount_per_unit_above_target(self):
        line = self._create_analytic_line(amount=-300.0, unit_amount=2.0)
        self.assertEqual(line.egd_target_value, 100.0)
        self.assertTrue(line.egd_target_above)

    def test_egd_target_above_false_when_amount_per_unit_below_target(self):
        line = self._create_analytic_line(amount=-150.0, unit_amount=2.0)
        self.assertEqual(line.egd_target_value, 100.0)
        self.assertFalse(line.egd_target_above)

    def test_egd_target_value_zero_when_no_product_or_positive_amount(self):
        line_no_product = self.env["account.analytic.line"].create(
            {
                "name": "No Product",
                "account_id": self.analytic_account.id,
                "unit_amount": 2.0,
                "amount": -200.0,
            }
        )

        self.assertEqual(line_no_product.egd_target_value, 0.0)
        self.assertFalse(line_no_product.egd_target_above)

        line_positive_amount = self._create_analytic_line(amount=200.0, unit_amount=2.0)

        self.assertEqual(line_positive_amount.egd_target_value, 0.0)
        self.assertFalse(line_positive_amount.egd_target_above)
