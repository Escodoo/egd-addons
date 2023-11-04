# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    egd_expiration_date = fields.Date(string="Expiration Date")
