# 2. Atributos de qualidade

Os atributos e a análise do trade-off seguem as seções 2.3 e 2.4 de [Abreu (2026)](8-conclusao.md#referências), com base no modelo de qualidade da [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html).

| Atributo | Por que foi priorizado | Decisão | Medida observável |
| --- | --- | --- | --- |
| Confiabilidade | Perder histórico quebra o acompanhamento. Essa necessidade é mais imediata que interoperar com outro sistema. | [ADR 0002](../adrs/0002-sqlite.md) | Uma transição válida acrescenta exatamente uma linha de histórico. Uma gravação com versão desatualizada acrescenta zero. |
| Manutenibilidade | Os prazos de prova e rotina variam. Isolar a política tem efeito mais imediato que construir versões para ambientes distintos. | [ADR 0003](../adrs/0003-portas.md) e [ADR 0005](../adrs/0005-politicas.md) | Introduzir uma política exige implementar o contrato e registrá-la na CLI. O serviço de chamados continua com a mesma operação de abertura. |
| Eficiência de desempenho | A fila é consultada repetidamente durante triagem. O tempo de consulta pesa mais que a capacidade de integrar vários departamentos no escopo atual. | [ADR 0001](../adrs/0001-monolito.md) e [ADR 0002](../adrs/0002-sqlite.md) | Meta de p95 até 100 ms para calcular a fila de 1.000 pendências no processo. Em 30 medições com SQLite em memória, o p95 observado foi 5,37 ms. O ensaio exclui inicialização da CLI, disco e renderização. |

## Confiabilidade

A atualização verifica a versão anterior e grava o histórico na mesma transação.

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

## Manutenibilidade

O serviço usa o prazo fornecido pela política escolhida.

```python
    due_at=policy.deadline(severity, opened_at),
)
self.writer.insert(ticket, HistoryEntry(ticket.id, ticket.status, opened_at, "Abertura"))
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L73-L75).

## Eficiência de desempenho

A consulta traz as pendências e a ordenação ocorre no próprio processo.

```python
def triage_queue(reader: QueueReader) -> list[Ticket]:
    return sorted(
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L85-L86).

## Trade-off

A transação de chamado e histórico favorece a consistência. O SQLite serializa escritores, o que limita vazão sob muitos atendimentos simultâneos. Aceitamos esse custo pelo volume de uma equipe pequena. O processo espera até cinco segundos pelo acesso ao banco antes de tratar a falha.

```python
    with closing(sqlite3.connect(args.banco, timeout=5.0)) as connection:
        run_command(args, SqliteTickets(connection))
except (TicketError, sqlite3.Error) as error:
    log_event(args.command, "error", error_type=type(error).__name__)
```

[Ver código em `chamados/cli.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/cli.py#L81-L84).
