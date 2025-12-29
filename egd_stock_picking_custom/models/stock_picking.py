# Copyright 2023 - TODAY, Rodrigo Neves Trindade <rodrigo.trindade@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    egd_responsible_id = fields.Many2one(
        string="Responsible for Custody",
        comodel_name="hr.employee",
    )
