# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests import common

RPS_INFO = {
    "cnpj": "00033767000117",
    "inscricao_municipal": "89887",
    "data_emissao": "2026-10-09T11:35:21",
    "natureza_operacao": "1",
    "optante_simples_nacional": "1",
    "regime_especial_tributacao": "0",
}

SERVICE_INFO = {
    "valor_servicos": 142479.83,
    "aliquota": 0.05,
    "iss_retido": "1",
    "municipio_prestacao_servico": "3550308",
    "discriminacao": "Serviços de Engenharia para manutenção corretiva",
    "codigo_tributacao_nacional": "070201",
}

RECIPIENT_INFO = {
    "cnpj": "43776517036613",
    "razao_social": "Companhia de Saneamento Basico do Estado de Sao Paulo",
    "codigo_municipio": "3550308",
    "endereco": "Jose Rafaeli",
    "numero": "284",
    "bairro": "Socorro",
    "cep": "04763280",
}


class TestL10nBrFiscalImovel(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")
        cls.company.city_id = cls.env.ref("l10n_br_base.city_3550308")
        cls.nfse_nacional = cls.env["focusnfe.nfse.nacional"]
        cls.imovel = cls.env["l10n_br_fiscal.imovel"].create(
            {
                "name": "Imóvel Costa Carvalho",
                "company_id": cls.company.id,
                "street_name": "Costa Carvalho",
                "street_number": "300",
                "district": "Pinheiros",
                "zip": "05429000",
                "city_id": cls.env.ref("l10n_br_base.city_3550308").id,
            }
        )

    def test_prepare_imovel_data_address_only(self):
        result = self.imovel._prepare_imovel_data()

        self.assertEqual(
            result,
            {
                "logradouro_imovel": "Costa Carvalho",
                "numero_imovel": "300",
                "bairro_imovel": "Pinheiros",
                "cep_imovel": "05429000",
            },
        )

    def test_prepare_imovel_data_with_registration_and_cib(self):
        imovel = self.imovel.copy(
            {"property_registration": "987654", "cib": "123.456.789-0"}
        )

        result = imovel._prepare_imovel_data()

        self.assertEqual(result.get("inscricao_imobiliaria_imovel"), "987654")
        self.assertEqual(result.get("codigo_cib_imovel"), "123.456.789-0")

    def test_prepare_dados_servico_merges_imovel_data(self):
        document = self.env.ref("l10n_br_fiscal.demo_nfse_same_state")
        document.imovel_id = self.imovel

        with patch(
            "odoo.addons.l10n_br_nfse.models.document.Document."
            "_prepare_dados_servico",
            return_value={"valor_servicos": 100.0},
        ):
            result = document._prepare_dados_servico()

        self.assertEqual(result["valor_servicos"], 100.0)
        self.assertEqual(result["imovel_data"], self.imovel._prepare_imovel_data())

    def test_prepare_dados_servico_without_imovel_unaffected(self):
        document = self.env.ref("l10n_br_fiscal.demo_nfse_same_state")
        document.imovel_id = False

        with patch(
            "odoo.addons.l10n_br_nfse.models.document.Document."
            "_prepare_dados_servico",
            return_value={"valor_servicos": 100.0},
        ):
            result = document._prepare_dados_servico()

        self.assertEqual(result, {"valor_servicos": 100.0})
        self.assertNotIn("imovel_data", result)

    def test_onchange_imovel_id_sets_issqn_fg_city_id(self):
        other_city = self.env.ref("l10n_br_base.city_3304557")
        imovel = self.imovel.copy({"city_id": other_city.id})
        document = self.env.ref("l10n_br_fiscal.demo_nfse_same_state")
        document.fiscal_line_ids.issqn_fg_city_id = self.company.city_id

        document.imovel_id = imovel
        document._onchange_imovel_id()

        self.assertEqual(document.fiscal_line_ids.issqn_fg_city_id, other_city)

    def test_prepare_payload_nacional_with_imovel(self):
        service = dict(SERVICE_INFO)
        service["imovel_data"] = self.imovel._prepare_imovel_data()
        edoc = {
            "rps": dict(RPS_INFO),
            "service": service,
            "recipient": dict(RECIPIENT_INFO),
        }

        vals = self.nfse_nacional._prepare_payload_nacional(edoc, self.company)

        self.assertEqual(vals.get("logradouro_imovel"), "Costa Carvalho")
        self.assertEqual(vals.get("numero_imovel"), "300")
        self.assertEqual(vals.get("bairro_imovel"), "Pinheiros")
        self.assertEqual(vals.get("cep_imovel"), "05429000")
