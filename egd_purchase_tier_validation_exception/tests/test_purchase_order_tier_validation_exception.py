# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPurchaseOrderTierValidationException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Service", "type": "service"}
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_qty": 1.0,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        cls.order_line = cls.purchase_order.order_line

        # Confirm the order so it reaches the "purchase" state, same as a
        # real order that already went through approval.
        cls.purchase_order.button_confirm()

        # Simulate a (historical, already approved) Tier Validation review,
        # without needing a full tier.definition evaluation flow.
        cls.env["tier.review"].create(
            {
                "model": "purchase.order",
                "res_id": cls.purchase_order.id,
                "status": "approved",
            }
        )
        cls.purchase_order.invalidate_recordset(["validation_status"])

    def test_validation_status_is_validated(self):
        """Sanity check: the order is under the exact condition that used
        to lock every field once any tier.validation.exception exists."""
        self.assertEqual(self.purchase_order.state, "purchase")
        self.assertEqual(self.purchase_order.validation_status, "validated")

    def test_qty_received_is_editable_after_validation(self):
        """The whole point of the module: order_line (and therefore
        qty_received) must stay writable even after Tier Validation."""
        self.purchase_order.write(
            {
                "order_line": [
                    (1, self.order_line.id, {"qty_received_manual": 1.0}),
                ],
            }
        )
        self.assertEqual(self.order_line.qty_received, 1.0)

    def test_button_approve_rewrite_does_not_raise(self):
        """Regression test for the incident caused by this module: once a
        tier.validation.exception exists for purchase.order, re-running the
        same write button_approve/button_confirm perform (state +
        date_approve) must not be blocked for orders already validated."""
        try:
            self.purchase_order.write(
                {
                    "state": "purchase",
                    "date_approve": self.purchase_order.date_approve,
                }
            )
        except ValidationError:
            self.fail(
                "Writing state/date_approve on an already validated "
                "purchase order should not raise, otherwise re-confirming "
                "already approved orders breaks (HT02341)."
            )

    def test_unrelated_field_still_blocked_after_validation(self):
        """Make sure the exception stays scoped: fields that were not
        explicitly excepted must still be locked after validation, so we
        don't silently widen the hole beyond what is needed."""
        with self.assertRaises(ValidationError):
            self.purchase_order.write({"partner_ref": "should not be allowed"})
