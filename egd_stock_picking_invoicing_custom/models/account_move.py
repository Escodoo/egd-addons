# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    production_date = fields.Date(
        string="Production Date",
        readonly=True,
        compute="_compute_production_date",
        store=True,
    )

    @api.depends("invoice_line_ids.sale_line_ids.order_id")
    def _compute_production_date(self):
        for move in self:
            sale_order = move.invoice_line_ids.sale_line_ids.mapped("order_id")
            move.production_date = (
                sale_order[0].production_date if sale_order else False
            )

    def action_post(self):
        res = super().action_post()
        for move in self:
            if move.production_date:
                move.line_ids.analytic_line_ids.write({"date": move.production_date})
        return res
