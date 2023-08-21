# Copyright TODAY Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EgdStockProductLotCustom(models.Model):
    _inherit = "stock.production.lot"

    certificado = fields.Char(
        string="Número de Certificado",
    )
