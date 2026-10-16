# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestRevisionLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Revision Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Revision Product", "type": "consu"}
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Revision Pricelist"}
        )
        cls.Wizard = cls.env["sale.blanket.order.revision.wizard"]

    def _create_blanket_order(self, **values):
        vals = {
            "partner_id": self.partner.id,
            "validity_date": date.today() + timedelta(days=30),
            "pricelist_id": self.pricelist.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom": self.product.uom_id.id,
                        "original_uom_qty": 10.0,
                        "price_unit": 100.0,
                    },
                )
            ],
        }
        vals.update(values)
        return self.env["sale.blanket.order"].create(vals)

    def _revise(self, blanket_order):
        wizard = self.Wizard.with_context(
            default_blanket_order_id=blanket_order.id
        ).create({})
        wizard.create_revision()
        revision = wizard.new_blanket_order_id
        # The wizard is a transient record, removed by the vacuum cleaner
        wizard.unlink()
        return revision

    def test_revision_numbering_survives_the_wizard(self):
        blanket_order = self._create_blanket_order()
        blanket_order.action_confirm()
        name = blanket_order.name

        revision_1 = self._revise(blanket_order)
        self.assertEqual(revision_1.name, f"{name} (Rev 1)")
        self.assertEqual(revision_1.revised_from_id, blanket_order)
        self.assertEqual(blanket_order.revision_count, 1)
        self.assertEqual(blanket_order.revision_ids, revision_1)

        revision_2 = self._revise(revision_1)
        self.assertEqual(revision_2.name, f"{name} (Rev 2)")
        self.assertEqual(revision_2.revised_from_id, revision_1)
        self.assertEqual(revision_2._get_revision_number(), 2)

        action = blanket_order.action_view_revisions()
        self.assertEqual(action["domain"], [("id", "in", revision_1.ids)])
        with self.assertRaises(UserError):
            blanket_order.set_to_draft()

    def test_link_revisions_by_name(self):
        original = self._create_blanket_order(name="BO/2024/0050")
        revision_1 = self._create_blanket_order(name="BO/2024/0050 (Rev 1)")
        revision_2 = self._create_blanket_order(name="BO/2024/0050 (Rev 2)")
        orphan = self._create_blanket_order(name="BO/2024/0099 (Rev 3)")

        self.env["sale.blanket.order"]._link_revisions_by_name()

        self.assertFalse(original.revised_from_id)
        self.assertEqual(revision_1.revised_from_id, original)
        self.assertEqual(revision_2.revised_from_id, revision_1)
        self.assertFalse(orphan.revised_from_id)
        self.assertEqual(original.revision_count, 1)
