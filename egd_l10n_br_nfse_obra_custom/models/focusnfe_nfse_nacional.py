# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class FocusnfeNfseNacional(models.AbstractModel):
    _inherit = "focusnfe.nfse.nacional"

    def _prepare_payload_nacional(self, edoc, company):
        vals = super()._prepare_payload_nacional(edoc, company)
        service_info = edoc.get("service", {})
        obra_data = service_info.get("obra_data")
        if obra_data:
            vals.update(obra_data)
        return vals
