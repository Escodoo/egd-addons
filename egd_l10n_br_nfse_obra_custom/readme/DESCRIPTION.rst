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
