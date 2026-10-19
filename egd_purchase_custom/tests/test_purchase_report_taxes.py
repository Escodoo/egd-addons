# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import html

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPurchaseReportTaxes(AccountTestInvoicingCommon):
    def _render_tax_labels(self, taxes):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": "Report tax labels",
                            "product_qty": 1,
                            "product_uom": self.product_a.uom_po_id.id,
                            "price_unit": 100,
                            "taxes_id": [Command.set(taxes.ids)],
                        }
                    )
                ],
            }
        )
        content, _ = self.env["ir.actions.report"]._render_qweb_html(
            "purchase.action_report_purchase_order", order.ids
        )
        cells = html.fromstring(content).xpath("//td[@name='td_taxes']")
        self.assertEqual(len(cells), 1)
        return cells[0].text_content().strip()

    def _tax(self, name, description, sequence):
        return self.env["account.tax"].create(
            {
                "name": name,
                "description": description,
                "amount": 1,
                "type_tax_use": "purchase",
                "sequence": sequence,
            }
        )

    def test_repeated_descriptions_are_shown_once_in_order(self):
        first = self._tax("Tax A", "Repeated tax", 1)
        second = self._tax("Tax B", "Repeated tax", 2)
        third = self._tax("Tax C", "Other tax", 3)
        self.assertEqual(
            self._render_tax_labels(first | second | third),
            "Repeated tax, Other tax",
        )

    def test_tax_name_is_used_without_a_description(self):
        tax = self._tax("Tax without description", False, 1)
        self.assertEqual(self._render_tax_labels(tax), tax.name)

    def test_line_without_taxes(self):
        self.assertEqual(self._render_tax_labels(self.env["account.tax"]), "")
