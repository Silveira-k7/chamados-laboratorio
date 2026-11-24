# ADR 0005 · Selecionar a política de prazo por chamado

## Status

Proposto

## Contexto

O mesmo incidente crítico pede prazos distintos em dia regular e durante prova. A data de vencimento orienta a fila durante todo o ciclo de atendimento.

## Decisão

Selecionar a Strategy na abertura e persistir o nome da política e o prazo efetivo do chamado.

## Alternativas consideradas

Uma matriz condicional no serviço acoplaria regras de calendário à abertura. Uma tabela editável em banco exigiria administrar configurações fora do repositório.

## Consequências

- **Positiva** · O serviço reutiliza o fluxo de abertura e a mudança de regra não altera prazos antigos.
- **Negativa** · Novas políticas exigem mudança de código e é responsabilidade do operador selecionar a opção adequada.

## Implementação

[PR #1](https://github.com/Silveira-k7/chamados-laboratorio/pull/1).

```python
    due_at=policy.deadline(severity, opened_at),
)
self.writer.insert(ticket, HistoryEntry(ticket.id, ticket.status, opened_at, "Abertura"))
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L73-L75).
