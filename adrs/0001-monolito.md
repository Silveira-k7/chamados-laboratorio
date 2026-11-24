# ADR 0001 · Monólito em camadas

## Status

Proposto. Aguarda a revisão da implementação pelo grupo.

## Contexto

A rotina registra e consulta chamados em um único posto de suporte.

## Decisão

Executar a CLI, a aplicação e a persistência dentro de um único processo.

## Alternativas consideradas

Microsserviços exigiriam deploys separados e chamadas remotas. Eventos assíncronos exigiriam entrega e deduplicação de mensagens na gravação.

## Consequências

- **Positiva** · A implantação cabe em um único repositório e as chamadas ficam no processo.
- **Negativa** · Atualizações são feitas para o sistema inteiro e a aplicação não escala componentes separadamente.

## Implementação

[PR #1](https://github.com/Silveira-k7/chamados-laboratorio/pull/1).

```python
with closing(sqlite3.connect(args.banco, timeout=5.0)) as connection:
    run_command(args, SqliteTickets(connection))
```

[Ver código em `chamados/cli.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/cli.py#L81-L82).
