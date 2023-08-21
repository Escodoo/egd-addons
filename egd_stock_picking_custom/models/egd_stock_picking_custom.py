# Copyright TODAY Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class EgdStockPickingCustom(models.Model):
    _inherit = "stock.picking"

    responsable = fields.Many2one(
        string="Responsável da Cautela",
        comodel_name="hr.employee",
    )
