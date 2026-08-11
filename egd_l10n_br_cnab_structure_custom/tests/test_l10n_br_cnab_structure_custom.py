# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestL10nBrCnabStructureCustom(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(
        cls, chart_template_ref="l10n_br_coa_generic.l10n_br_coa_generic_template"
    ):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.company_data["company"]
        cls.env.user.company_id = cls.company.id
        cls.payment_method_out = cls.env.ref(
            "l10n_br_account_payment_order.payment_mode_type_cnab240_out"
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "bank_account_link": "fixed",
                "name": "CNAB 240 Outbound",
                "company_id": cls.company.id,
                "payment_method_id": cls.payment_method_out.id,
                "payment_order_ok": True,
                "fixed_journal_id": cls.company_data["default_journal_bank"].id,
            }
        )

    def _create_invoice(self, barcode=None):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner_a.id,
                "move_type": "in_invoice",
                "ref": "Test Bill Barcode",
                "invoice_date": fields.Date.today(),
                "company_id": self.company.id,
                "payment_mode_id": self.payment_mode.id,
                "journal_id": self.company_data["default_journal_purchase"].id,
                "barcode": barcode,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        return invoice

    def _create_payment_order(self, invoice):
        invoice.action_post()
        invoice.create_account_payment_line()
        payment_order = self.env["account.payment.order"].search(
            [
                ("payment_type", "=", "outbound"),
                ("company_id", "=", self.company.id),
            ]
        )
        return payment_order

    def test_barcode_field_exists(self):
        invoice = self._create_invoice()
        self.assertTrue(hasattr(invoice, "barcode"))
        self.assertFalse(invoice.barcode)

    def test_barcode_copied_to_payment_line(self):
        barcode = "12345678901234567890"
        invoice = self._create_invoice(barcode=barcode)
        payment_order = self._create_payment_order(invoice)
        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertEqual(payment_order.payment_line_ids.barcode, barcode)

    def test_payment_line_without_barcode(self):
        invoice = self._create_invoice()
        payment_order = self._create_payment_order(invoice)
        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertFalse(payment_order.payment_line_ids.barcode)
