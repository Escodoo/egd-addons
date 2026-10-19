# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    barcode = fields.Char(
        help="This field is used in the payment of supplier slips",
    )

    payment_type = fields.Selection(
        related="payment_mode_id.payment_type",
    )
