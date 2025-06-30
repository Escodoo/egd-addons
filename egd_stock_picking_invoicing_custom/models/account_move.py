# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    production_date = fields.Date(
        string="Production Date",
        readonly=True,
        compute="_compute_production_date",
    )

    @api.depends("invoice_line_ids.sale_line_ids.order_id")
    def _compute_production_date(self):
        for move in self:
            sale_order = move.invoice_line_ids.sale_line_ids.mapped("order_id")
            stock_picking = move.stock_move_id.picking_id
            production_date = False
            if sale_order:
                move.production_date = sale_order[0].production_date
            elif stock_picking:
                move.production_date = stock_picking.production_date
            move.production_date = production_date

    def _post(self, soft=True):
        res = super()._post(soft=soft)
        for move in self:
            if move.production_date:
                move.line_ids.analytic_line_ids.write({"date": move.production_date})
        return res
