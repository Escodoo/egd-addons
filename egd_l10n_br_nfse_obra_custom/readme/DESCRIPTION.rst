This module adds an "Obra" (construction site) record with a CNO/CEI code,
a property registration (inscrição imobiliária) code, an ART and an
address. The Obra can be selected on the customer invoice, and its data is
sent to Focus NFe in the NFSe Nacional payload as required by the Sistema
Nacional NFS-e for civil construction services (LC 116 service list
subitems such as 7.02, 7.04, 7.05, 7.06, 7.07, 7.08, 7.17, 7.19 and
14.14.03/14.14.04).

The Sistema Nacional NFS-e obra group (``infDPS/serv/obra``) only accepts
one of ``cObra``, ``inscImobFisc`` or ``end`` at a time (it is an
``xs:choice`` in the DPS schema). The Obra record has an "Identification
Type" field to select which one is sent:

* **CNO/CEI**: sent as ``codigo_obra``.
* **Property Registration**: sent as ``inscricao_imobiliaria``.
* **Address**: sent as ``logradouro_obra``/``numero_obra``/
  ``complemento_obra``/``bairro_obra``/``cep_obra``.

This module also adds an "Imóvel" (real estate property) record with a
city, an address, an optional inscrição imobiliária fiscal and an
optional CIB (Cadastro Imobiliário Brasileiro) code. The Imóvel can be
selected on the customer invoice, and its data is sent to Focus NFe in
the NFSe Nacional payload as the ``imovel`` group required by the
Sistema Nacional NFS-e when the operation indicator
(``codigo_indicador_operacao``/``cIndOp``) refers to an operation on
real estate property (codes starting with ``02``, e.g. ``020201`` -
Serviço sobre bem imóvel). Without this group, Focus NFe/Sefin Nacional
rejects the DPS with error ``E0932``.

The Imóvel address is always sent as ``logradouro_imovel``/
``numero_imovel``/``complemento_imovel``/``bairro_imovel``/
``cep_imovel``, with ``inscricao_imobiliaria_imovel`` and
``codigo_cib_imovel`` added when filled in.

The Sistema Nacional NFS-e also requires the service location city
(``codigo_municipio_prestacao``) to match the Imóvel's city for these
operation indicators. Selecting an Imóvel on the invoice automatically
updates the fiscal lines' service location city to match, to help avoid
this mismatch (which Sefin Nacional rejects with the same generic
``E0932`` error, without indicating the real cause).
