# 8. Padrão transversal

## Observabilidade · Logs estruturados

A seção 18.5 de [Abreu (2026)](8-conclusao.md#referências), na página 153, descreve logs estruturados como eventos com campos consultáveis. Na triagem em linha de comando, operadores precisam saber se a rotina foi concluída e distinguir erros de regras de negócio de falhas de armazenamento. Cada comando reconhecido emite um evento JSON com instante UTC, ação e resultado. Falhas incluem também a classe do erro. Os registros saem em `stderr` e permitem filtrar por operação ou resultado enquanto a saída normal segue em `stdout`.

```python
def log_event(command: str, outcome: str, *, error_type: str | None = None) -> None:
    event = {
        "event": "ticket_command",
        "timestamp": datetime.now(UTC).isoformat(),
        "command": command,
        "outcome": outcome,
    }
    if error_type:
        event["error_type"] = error_type
    level = logging.ERROR if error_type else logging.INFO
    LOGGER.log(level, "%s", json.dumps(event))
```

[Ver código em `chamados/cli.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/cli.py#L64-L75).

Exemplo de verificação. `python -m chamados iniciar inexistente 2>logs.txt` gera o evento `ticket_command` com `outcome=error` e `error_type=TicketError`, além da mensagem textual de erro. A decisão de implantação local está no [ADR 0004](../adrs/0004-implantacao-local.md).
