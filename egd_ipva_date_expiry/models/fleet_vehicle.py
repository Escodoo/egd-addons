# Copyright 2024 - TODAY, Matheus Marques <matheus.marques@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models


class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    ipva_expiry_date = fields.Date(string="IPVA Expiry Date", store="True")
    ipva_near_expiry = fields.Boolean(
        string="IPVA Near Expiry", compute="_compute_ipva_near_expiry"
    )

    @api.depends("ipva_expiry_date")
    def _compute_ipva_near_expiry(self):
        for vehicle in self:
            if vehicle.ipva_expiry_date:
                expiry_date = fields.Date.from_string(vehicle.ipva_expiry_date)
                if expiry_date - datetime.now().date() <= timedelta(days=30):
                    vehicle.ipva_near_expiry = True
                else:
                    vehicle.ipva_near_expiry = False
            else:
                vehicle.ipva_near_expiry = False
