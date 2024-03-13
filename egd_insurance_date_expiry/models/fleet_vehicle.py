# Copyright 2024 - TODAY, Matheus Marques <matheus.marques@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    insurance_date_expiry = fields.Date(string="Insurance expiry date")
    insurance_near_expiry = fields.Boolean(
        string="insurance Near Expiry", compute="_compute_insurance_near_expiry"
    )

    @api.depends("insurance_date_expiry")
    def _compute_insurance_near_expiry(self):
        for vehicle in self:
            if vehicle.insurance_date_expiry:
                expiry_date = fields.Date.from_string(vehicle.insurance_date_expiry)
                if expiry_date - datetime.now().date() <= timedelta(days=30):
                    vehicle.insurance_near_expiry = True
                else:
                    vehicle.insurance_near_expiry = False
            else:
                vehicle.insurance_near_expiry = False
