# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


@common.tagged("post_install", "-at_install")
class TestPurchaseRequestLine(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.product = self.env["product.product"].create(
            {"name": "Requested product", "standard_price": 12.5}
        )
        self.account = self.env["account.analytic.account"].create(
            {"name": "Request cost target"}
        )
        self.request = self.env["purchase.request"].create({})
        self.Line = self.env["purchase.request.line"]

    def _line_vals(self, quantity, **overrides):
        vals = {
            "request_id": self.request.id,
            "name": self.product.name,
            "product_id": self.product.id,
            "product_uom_id": self.product.uom_id.id,
            "product_qty": quantity,
            "analytic_account_id": self.account.id,
        }
        vals.update(overrides)
        return vals

    def test_orm_cost_defaults_and_manual_override(self):
        line = self.Line.create(self._line_vals(2))
        self.assertEqual(line.egd_estimated_unit_cost, 12.5)
        self.assertEqual(line.estimated_cost, 25)
        line.egd_estimated_unit_cost = 20
        line.product_qty = 3
        self.assertEqual(line.egd_estimated_unit_cost, 20)
        self.assertEqual(line.estimated_cost, 60)
        other = self.Line.create(self._line_vals(2, egd_estimated_unit_cost=0))
        self.assertEqual(other.egd_estimated_unit_cost, 0)
        product = self.product.copy({"standard_price": 7})
        line.product_id = product
        self.assertEqual(line.egd_estimated_unit_cost, 7)

    def test_total_updates_after_quantity_change(self):
        first, second = self.Line.create([self._line_vals(3), self._line_vals(4)])
        self.assertEqual(first.egd_product_quantity_requested, 7)
        second.product_qty = 9
        self.assertEqual(first.egd_product_quantity_requested, 12)
        self.assertEqual(second.egd_product_quantity_requested, 12)

    def test_total_updates_across_requests_and_deletion(self):
        first = self.Line.create(self._line_vals(3))
        other_request = self.env["purchase.request"].create({})
        self.assertEqual(first.egd_product_quantity_requested, 3)
        second = self.Line.create(self._line_vals(4, request_id=other_request.id))
        self.assertEqual(first.egd_product_quantity_requested, 7)
        second.product_qty = 9
        self.assertEqual(first.egd_product_quantity_requested, 12)
        second.unlink()
        self.assertEqual(first.egd_product_quantity_requested, 3)

    def test_total_includes_unsaved_siblings(self):
        self.Line.create(self._line_vals(5))
        first_vals = self._line_vals(3)
        second_vals = self._line_vals(4)
        first_vals.pop("request_id")
        second_vals.pop("request_id")
        form = self.env["purchase.request"].new(
            {
                "line_ids": [
                    (0, 0, first_vals),
                    (0, 0, second_vals),
                ]
            }
        )
        first, second = form.line_ids
        self.assertEqual(first.egd_product_quantity_requested, 12)
        second.product_qty = 10
        self.assertEqual(first.egd_product_quantity_requested, 18)

    def test_total_replaces_saved_lines_with_form_values(self):
        self.Line.create([self._line_vals(3), self._line_vals(4)])
        form_vals = self._line_vals(10)
        form_vals.pop("request_id")
        form = self.env["purchase.request"].new(
            {"line_ids": [(0, 0, form_vals)]},
            origin=self.request,
        )
        self.assertEqual(len(form.line_ids), 1)
        self.assertEqual(form.line_ids.egd_product_quantity_requested, 10)
