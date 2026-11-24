# ADR 0003 · Separar camadas e definir portas de persistência

## Status

Proposto

## Contexto

Prazos e transições precisam evoluir sem mudanças no mecanismo de persistência. A aplicação precisa guardar dados localmente e os testes precisam controlar o instante de abertura.

## Decisão

Separar CLI, aplicação, domínio e persistência. Receber portas pequenas para leitura e gravação.

## Alternativas consideradas

Um módulo único aproximaria regras, I/O e SQL. Separar cada responsabilidade em pacote próprio ampliaria a árvore de módulos para um fluxo pequeno.

## Consequências

- **Positiva** · O fluxo usa um relógio injetado e pode ser executado com fonte de dados substituta em testes.
- **Negativa** · A composição dos objetos precisa ser explícita na inicialização.

## Implementação

[PR #1](https://github.com/Silveira-k7/chamados-laboratorio/pull/1).

```python
def __init__(self, reader: TicketReader, writer: TicketWriter, now: Callable[[], datetime]):
    self.reader = reader
    self.writer = writer
    self.now = now
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L55-L58).
