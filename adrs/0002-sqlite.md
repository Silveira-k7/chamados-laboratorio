# ADR 0002 · Persistir chamados e histórico em SQLite

## Status

Proposto

## Contexto

O histórico precisa refletir o estado salvo mesmo se uma gravação for interrompida. O sistema roda no posto de suporte e dois comandos podem ler o mesmo chamado antes de uma atualização.

## Decisão

Gravar chamado e histórico na mesma transação SQLite. Comparar a versão na atualização e usar chaves estrangeiras.

## Alternativas consideradas

Um arquivo JSON exigiria controle próprio de concorrência e atomicidade. PostgreSQL adicionaria operação de um banco externo.

## Consequências

- **Positiva** · Atualização e histórico são consistentes e o banco pode ser executado localmente.
- **Negativa** · As escritas são serializadas e o arquivo precisa de uma política operacional de cópia.

## Implementação

[PR #1](https://github.com/Silveira-k7/chamados-laboratorio/pull/1).

```python
def update(self, ticket: Ticket, entry: HistoryEntry) -> None:
    with self.connection:
        # A versão impede sobrescrever uma transição feita por outro operador.
        updated = self.connection.execute(
            "UPDATE tickets SET status = ?, version = ? WHERE id = ? AND version = ?",
            (ticket.status, ticket.version, ticket.id, ticket.version - 1),
        )
        if updated.rowcount != 1:
            raise TicketError(
                "O chamado mudou durante a operação. Consulte-o e tente novamente."
            )
        self._append(entry)
```

[Ver código em `chamados/storage.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/storage.py#L58-L69).
