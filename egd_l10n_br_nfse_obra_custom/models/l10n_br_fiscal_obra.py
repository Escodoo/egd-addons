# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from erpbrasil.base import misc

from odoo import fields, models


class L10nBrFiscalObra(models.Model):
    _name = "l10n_br_fiscal.obra"
    _description = "Obra (Construction Site)"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    identification_type = fields.Selection(
        selection=[
            ("cno_cei", "CNO/CEI"),
            ("property_registration", "Property Registration"),
            ("address", "Address"),
        ],
        required=True,
        default="cno_cei",
        help="The Sistema Nacional NFS-e obra group only accepts one of "
        "these three ways to identify the construction site at a time "
        "(cObra, inscImobFisc or end are an xs:choice in the DPS schema). "
        "This selects which one is sent.",
    )
    cno_cei = fields.Char(
        string="CNO/CEI",
        help="Cadastro Nacional de Obras / Cadastro Específico do INSS",
    )
    property_registration = fields.Char(
        help="Code issued by the City Hall to identify the construction "
        "site (inscrição imobiliária fiscal), used for property tax "
        "(IPTU) purposes.",
    )
    civil_construction_art = fields.Char(string="ART")
    street_name = fields.Char(string="Street")
    street_number = fields.Char(string="Number")
    street_number2 = fields.Char(string="Complement")
    district = fields.Char()
    zip = fields.Char()

    def _prepare_obra_data(self):
        self.ensure_one()
        if self.identification_type == "cno_cei" and self.cno_cei:
            return {"codigo_obra": misc.punctuation_rm(self.cno_cei)}
        if self.identification_type == "property_registration" and (
            self.property_registration
        ):
            return {"inscricao_imobiliaria": self.property_registration}
        if self.identification_type == "address" and self.street_name:
            return {
                "logradouro_obra": self.street_name,
                "numero_obra": self.street_number or "",
                "bairro_obra": self.district or "",
                "cep_obra": (
                    misc.punctuation_rm(self.zip).zfill(8) if self.zip else ""
                ),
                **(
                    {"complemento_obra": self.street_number2}
                    if self.street_number2
                    else {}
                ),
            }
        return {}
