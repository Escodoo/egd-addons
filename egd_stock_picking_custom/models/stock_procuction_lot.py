# Copyright 2023 - TODAY, Rodrigo Neves Trindade <rodrigo.trindade@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProcuctionLot(models.Model):

    _inherit = "stock.production.lot"

    egd_certification = fields.Char(
        string="Certificate Number",
    )
