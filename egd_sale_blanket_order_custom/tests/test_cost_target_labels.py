# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests.common import TransactionCase


class TestCostTargetLabels(TransactionCase):
    def test_cost_targets_are_direct_children_of_the_totals_group(self):
        view = self.env["sale.blanket.order"].get_view(
            view_id=self.env.ref("sale_blanket_order.view_blanket_order_form").id,
            view_type="form",
        )
        arch = etree.fromstring(view["arch"])
        totals = arch.xpath("//field[@name='amount_total']")[0]
        footer = totals.getparent().getparent()
        self.assertEqual(footer.tag, "group")
        self.assertIn("oe_subtotal_footer", footer.get("class", "").split())
        for name in ("egd_total_product_costs", "egd_total_service_costs"):
            fields = footer.xpath(f"./field[@name='{name}']")
            self.assertEqual(len(fields), 1)
            self.assertNotEqual(fields[0].get("nolabel"), "1")
        self.assertEqual(len(footer.xpath("./field[@name='egd_total_costs']")), 1)
        self.assertEqual(len(footer.xpath(".//label[@for='egd_total_costs']")), 1)
