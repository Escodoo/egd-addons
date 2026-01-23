# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from types import SimpleNamespace

from odoo.tests.common import TransactionCase

from odoo.addons.egd_stock_picking_invoicing_custom.models.account_move import (
    AccountMove,
)


class FakeOrderCollection:
    def __init__(self, orders):
        self._orders = orders

    def mapped(self, field_name):
        if field_name == "order_id":
            return self._orders
        return []


class TestAccountMoveProductionDate(TransactionCase):
    def _build_fake_move(self, sale_orders=None, picking_date=False):
        sale_orders = sale_orders or []
        return SimpleNamespace(
            invoice_line_ids=SimpleNamespace(
                sale_line_ids=FakeOrderCollection(sale_orders),
            ),
            stock_move_id=SimpleNamespace(
                picking_id=SimpleNamespace(production_date=picking_date)
            ),
            production_date=False,
        )

    def test_compute_production_date_from_sale_order(self):
        sale_order = SimpleNamespace(production_date="2026-03-10")
        move = self._build_fake_move(
            sale_orders=[sale_order],
            picking_date="2026-03-01",
        )

        AccountMove._compute_production_date([move])

        self.assertEqual(move.production_date, "2026-03-10")

    def test_compute_production_date_from_stock_picking(self):
        move = self._build_fake_move(
            sale_orders=[],
            picking_date="2026-03-12",
        )

        AccountMove._compute_production_date([move])

        self.assertEqual(move.production_date, "2026-03-12")

    def test_compute_production_date_without_sources(self):
        move = self._build_fake_move(
            sale_orders=[],
            picking_date=False,
        )

        AccountMove._compute_production_date([move])

        self.assertFalse(move.production_date)
