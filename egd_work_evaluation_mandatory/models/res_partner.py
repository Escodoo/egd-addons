# Copyright 2024 - TODAY, Matheus Marques <matheus.marques@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_evaluation_mandatory = fields.Boolean(
        string="Evaluation Mandatory", default=False
    )
