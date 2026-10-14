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


class TestL10nBrFiscalObra(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")
        cls.company.city_id = cls.env.ref("l10n_br_base.city_3550308")
        cls.nfse_nacional = cls.env["focusnfe.nfse.nacional"]
        cls.obra = cls.env["l10n_br_fiscal.obra"].create(
            {
                "name": "Obra Costa Carvalho",
                "company_id": cls.company.id,
                "identification_type": "address",
                "street_name": "Costa Carvalho",
                "street_number": "300",
                "district": "Pinheiros",
                "zip": "05429000",
            }
        )

    def test_prepare_obra_data_by_cno_cei(self):
        obra = self.obra.copy(
            {"identification_type": "cno_cei", "cno_cei": "123.456.78901/23"}
        )

        result = obra._prepare_obra_data()

        self.assertEqual(result, {"codigo_obra": "1234567890123"})

    def test_prepare_obra_data_by_property_registration(self):
        obra = self.obra.copy(
            {
                "identification_type": "property_registration",
                "property_registration": "987654",
            }
        )

        result = obra._prepare_obra_data()

        self.assertEqual(result, {"inscricao_imobiliaria": "987654"})

    def test_prepare_obra_data_by_address(self):
        result = self.obra._prepare_obra_data()

        self.assertEqual(
            result,
            {
                "logradouro_obra": "Costa Carvalho",
                "numero_obra": "300",
                "bairro_obra": "Pinheiros",
                "cep_obra": "05429000",
            },
        )

    def test_prepare_obra_data_ignores_unset_fields_for_the_chosen_type(self):
        # identification_type stays "cno_cei" but cno_cei is empty: the
        # xs:choice has nothing to report, so nothing must be sent, even
        # though the address fields happen to be filled on the record.
        obra = self.obra.copy({"identification_type": "cno_cei", "cno_cei": False})

        self.assertEqual(obra._prepare_obra_data(), {})

    def test_prepare_dados_servico_merges_obra_data(self):
        document = self.env.ref("l10n_br_fiscal.demo_nfse_same_state")
        document.obra_id = self.obra

        with patch(
            "odoo.addons.l10n_br_nfse.models.document.Document."
            "_prepare_dados_servico",
            return_value={"valor_servicos": 100.0},
        ):
            result = document._prepare_dados_servico()

        self.assertEqual(result["valor_servicos"], 100.0)
        self.assertEqual(result["obra_data"], self.obra._prepare_obra_data())

    def test_prepare_dados_servico_without_obra_unaffected(self):
        document = self.env.ref("l10n_br_fiscal.demo_nfse_same_state")
        document.obra_id = False

        with patch(
            "odoo.addons.l10n_br_nfse.models.document.Document."
            "_prepare_dados_servico",
            return_value={"valor_servicos": 100.0},
        ):
            result = document._prepare_dados_servico()

        self.assertEqual(result, {"valor_servicos": 100.0})
        self.assertNotIn("obra_data", result)

    def test_prepare_payload_nacional_without_obra(self):
        edoc = {
            "rps": dict(RPS_INFO),
            "service": dict(SERVICE_INFO),
            "recipient": dict(RECIPIENT_INFO),
        }

        vals = self.nfse_nacional._prepare_payload_nacional(edoc, self.company)

        self.assertNotIn("logradouro_obra", vals)
        self.assertNotIn("codigo_obra", vals)
        self.assertNotIn("inscricao_imobiliaria", vals)

    def test_prepare_payload_nacional_with_obra_address(self):
        service = dict(SERVICE_INFO)
        service["obra_data"] = self.obra._prepare_obra_data()
        edoc = {
            "rps": dict(RPS_INFO),
            "service": service,
            "recipient": dict(RECIPIENT_INFO),
        }

        vals = self.nfse_nacional._prepare_payload_nacional(edoc, self.company)

        self.assertEqual(vals.get("logradouro_obra"), "Costa Carvalho")
        self.assertEqual(vals.get("numero_obra"), "300")
        self.assertEqual(vals.get("bairro_obra"), "Pinheiros")
        self.assertEqual(vals.get("cep_obra"), "05429000")
        self.assertNotIn("codigo_obra", vals)

    def test_prepare_payload_nacional_with_obra_cno_cei(self):
        obra = self.obra.copy(
            {"identification_type": "cno_cei", "cno_cei": "123456789012"}
        )
        service = dict(SERVICE_INFO)
        service["obra_data"] = obra._prepare_obra_data()
        edoc = {
            "rps": dict(RPS_INFO),
            "service": service,
            "recipient": dict(RECIPIENT_INFO),
        }

        vals = self.nfse_nacional._prepare_payload_nacional(edoc, self.company)

        self.assertEqual(vals.get("codigo_obra"), "123456789012")
        self.assertNotIn("logradouro_obra", vals)
