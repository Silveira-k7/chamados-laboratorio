# 6. Clean Code

## Nomes claros, função pequena e poucos parâmetros

`triage_queue` recebe apenas a fonte da fila e define a ordem de triagem. `due_at` e `created_at` deixam claro quando se compara prazo e quando se compara abertura.

```python
def triage_queue(reader: QueueReader) -> list[Ticket]:
    return sorted(
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L85-L86).

## Duplicação

`_append` concentra a instrução de inserir no histórico, compartilhada pela abertura e pela transição. Uma alteração na representação do histórico tem um único ponto de escrita.

```python
def _append(self, entry: HistoryEntry) -> None:
    self.connection.execute(
        "INSERT INTO history (ticket_id, status, at, note) VALUES (?, ?, ?, ?)",
        (entry.ticket_id, entry.status, entry.at.isoformat(), entry.note),
    )
```

[Ver código em `chamados/storage.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/storage.py#L71-L75).

## Acoplamento e coesão

O serviço de aplicação recebe portas pequenas para os casos de uso. A conversão entre tipos do SQLite e tipos do domínio fica no adaptador.

```python
def __init__(self, reader: TicketReader, writer: TicketWriter, now: Callable[[], datetime]):
    self.reader = reader
    self.writer = writer
    self.now = now
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L55-L58).

## Comentário de motivo

A nota explica por que a atualização confere a versão, informação que o comando SQL por si só não conta.

```python
# A versão impede sobrescrever uma transição feita por outro operador.
updated = self.connection.execute(
    "UPDATE tickets SET status = ?, version = ? WHERE id = ? AND version = ?",
    (ticket.status, ticket.version, ticket.id, ticket.version - 1),
)
```

[Ver código em `chamados/storage.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/storage.py#L60-L64).

## Tratamento explícito de erros

A CLI diferencia falha de comando de uma operação bem-sucedida no retorno e registra a categoria do erro. Em caso de falha, a operação termina com código 1 e mensagem ao operador.

```python
except (TicketError, sqlite3.Error) as error:
    log_event(args.command, "error", error_type=type(error).__name__)
    print(f"Erro: {error}", file=sys.stderr)
    return 1
```

[Ver código em `chamados/cli.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/cli.py#L83-L86).

## Linter, formatador e testes

Ruff verifica erros de sintaxe e estilo selecionados (`E4`, `E7`, `E9`), problemas de nomes e imports (`F`, `I`), modernização para Python 3.11 (`UP`) e erros comuns (`B`). A configuração também define o limite convencional de comprimento para a formatação.

```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "I", "UP", "B"]
```

[Ver código em `pyproject.toml`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/pyproject.toml#L1-L6).

```bash
ruff check .
ruff format --check .
python -m unittest discover -s tests -v
```

Quatro testes de fluxo cobrem a ordem da triagem, o ciclo de atendimento, uma transição inválida e a rejeição de atualização com versão antiga. Um quinto teste [confere os imports entre as camadas](https://github.com/Silveira-k7/chamados-laboratorio/blob/dde43c9ca02c4584e898e59234092ab0829e34d2/tests/test_architecture.py#L35-L44). Acompanhe o resultado do [workflow de qualidade](https://github.com/Silveira-k7/chamados-laboratorio/actions/workflows/qualidade.yml) no PR e nos pushes ao `main`.

[Catálogo de code smells e técnicas de refatoração](https://refactoring.guru/pt-br/refactoring). A extração de `_append` é um exemplo de como evitar Código Duplicado neste fluxo.
