Este módulo resolve um conflito entre o ``base_tier_validation`` e o fluxo
obrigatório de avaliação de fornecedor (``egd_work_evaluation_mandatory``):
assim que um Pedido de Compra tem qualquer revisão (``review_ids``), mesmo
uma histórica já aprovada, o ``base_tier_validation`` trava todos os campos
de primeiro nível do pedido, incluindo o ``order_line``, impedindo qualquer
edição nas linhas, como registrar a *Quantidade Recebida* real no momento
do recebimento.

Dados Adicionados
------------------

- Um registro de ``tier.validation.exception`` que exclui o ``order_line``
  dessa trava automática, permitindo abrir/editar as linhas novamente em
  pedidos já sob ou após a Validação por Camadas. O mesmo registro também
  inclui ``state`` e ``date_approve``: assim que existe qualquer exceção
  para o modelo, o ``base_tier_validation`` passa a exigir que **todos**
  os campos de cada ``write()`` estejam na lista de exceção — e
  ``button_confirm``/``button_approve`` escrevem justamente esses dois
  campos, então sem eles a confirmação de pedidos já aprovados passava a
  falhar.

Customizações de View Adicionadas
----------------------------------

- Como destravar o ``order_line`` como um todo também destravaria o
  ``price_unit`` (ele não tem nenhuma trava por estado própria), é
  reintroduzida uma condição de readonly ligada ao ``review_ids`` do pedido
  nesse campo, mantendo-o travado. ``product_id`` e ``product_uom`` já
  mantêm sua própria trava por estado, sem alteração, e o ``qty_received``
  é deixado propositalmente intocado, já que é o único campo que deve
  continuar editável.
