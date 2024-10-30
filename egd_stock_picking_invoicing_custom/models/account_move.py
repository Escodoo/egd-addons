# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    production_date = fields.Date(string="Production Date", readonly=True)

    def action_post(self):
        res = super().action_post()
        for move in self:
            if move.production_date:
                move.line_ids.analytic_line_ids.write({"date": move.production_date})
        return res
