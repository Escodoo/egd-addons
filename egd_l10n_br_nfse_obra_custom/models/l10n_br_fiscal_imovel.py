# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from erpbrasil.base import misc

from odoo import fields, models


class L10nBrFiscalImovel(models.Model):
    _name = "l10n_br_fiscal.imovel"
    _description = "Imóvel (Real Estate Property)"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    property_registration = fields.Char(
        help="Inscrição imobiliária fiscal issued by the City Hall to "
        "identify the property, used for property tax (IPTU) purposes.",
    )
    cib = fields.Char(
        string="CIB",
        help="Código do Cadastro Imobiliário Brasileiro (CIB) of the property.",
    )
    street_name = fields.Char(string="Street", required=True)
    street_number = fields.Char(string="Number")
    street_number2 = fields.Char(string="Complement")
    district = fields.Char()
    zip = fields.Char()
    city_id = fields.Many2one(
        comodel_name="res.city",
        string="City",
        required=True,
        help="Município onde o imóvel está localizado. O Sistema Nacional "
        "NFS-e exige que o município de prestação do serviço seja igual "
        "ao município do imóvel para indicadores de operação relacionados "
        "a bem imóvel (ex.: 020201).",
    )

    def _prepare_imovel_data(self):
        self.ensure_one()
        result = {
            "logradouro_imovel": self.street_name,
            "numero_imovel": self.street_number or "",
            "bairro_imovel": self.district or "",
            "cep_imovel": (misc.punctuation_rm(self.zip).zfill(8) if self.zip else ""),
        }
        if self.street_number2:
            result["complemento_imovel"] = self.street_number2
        if self.property_registration:
            result["inscricao_imobiliaria_imovel"] = self.property_registration
        if self.cib:
            result["codigo_cib_imovel"] = self.cib
        return result
