# ADR 0004 · Implantação local em Python

## Status

Proposto. Aguarda a revisão da implementação pelo grupo.

## Contexto

A equipe alvo precisa iniciar o fluxo de triagem em um posto sem provisionar um servidor.

## Decisão

Distribuir o código no GitHub como módulo executável por Python 3.11, com SQLite local. Registrar eventos JSON em stderr.

## Alternativas consideradas

Contêiner exigiria instalar e operar um runtime adicional. Hospedagem de uma API exigiria deploy, autenticação e disponibilidade de rede.

## Consequências

- **Positiva** · A execução exige apenas a biblioteca padrão e permite redirecionar os logs para análise.
- **Negativa** · Cada instalação opera com seu próprio arquivo e não há acesso remoto multiusuário.

## Implementação

[PR #1](https://github.com/Silveira-k7/chamados-laboratorio/pull/1).

```python
    with closing(sqlite3.connect(args.banco, timeout=5.0)) as connection:
        run_command(args, SqliteTickets(connection))
except (TicketError, sqlite3.Error) as error:
    log_event(args.command, "error", error_type=type(error).__name__)
```

[Ver código em `chamados/cli.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/cli.py#L81-L84).
