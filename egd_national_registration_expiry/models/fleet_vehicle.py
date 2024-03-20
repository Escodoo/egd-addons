# Copyright 2024 - TODAY, Matheus Marques <matheus.marques@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models


class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    renavam_number = fields.Char(string="Renavam number")
    renavam_validity = fields.Date(string="Renavam expiry")
    renavam_near_expiry = fields.Boolean(
        string="renavam Near Expiry", compute="_compute_renavam_near_expiry"
    )

    @api.depends("renavam_validity")
    def _compute_renavam_near_expiry(self):
        for vehicle in self:
            if vehicle.renavam_validity:
                expiry_date = fields.Date.from_string(vehicle.renavam_validity)
                if expiry_date - datetime.now().date() <= timedelta(days=30):
                    vehicle.renavam_near_expiry = True
                else:
                    vehicle.renavam_near_expiry = False
            else:
                vehicle.renavam_near_expiry = False
