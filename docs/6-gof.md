# 7. Padrões GoF

## Strategy · Comportamental

**Problema.** Um chamado crítico aberto em dia de prova tem um prazo de 30 minutos, enquanto a política regular dá quatro horas. As duas políticas usam o mesmo fluxo de abertura.

```python
    due_at=policy.deadline(severity, opened_at),
)
self.writer.insert(ticket, HistoryEntry(ticket.id, ticket.status, opened_at, "Abertura"))
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L73-L75).

**Benefício.** Cada política mantém suas regras e pode ser escolhida por chamado. **Custo.** O operador precisa indicar a política quando há prova e o ponto de entrada registra as implementações disponíveis.

[Diagrama de classes · Strategy](../diagrams/classes-strategy.md) · [Refactoring Guru](https://refactoring.guru/pt-br/design-patterns/strategy)

## State · Comportamental

**Problema.** O significado de uma operação muda com o estado do chamado. A resolução exige uma solução registrada, a reabertura exige motivo e um chamado recém-aberto não pode pular diretamente para resolvido.

```python
def advance(self, action: Action, note: str) -> "Ticket":
    next_status = STATES[self.status].transition(action, note.strip())
    return replace(self, status=next_status, version=self.version + 1)
```

[Ver código em `chamados/domain.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/domain.py#L41-L43).

```python
class InProgressState:
    def transition(self, action: Action, note: str) -> Status:
        if action is not Action.RESOLVE:
            raise TicketError("Chamado em atendimento só pode ser resolvido.")
        if not note:
            raise TicketError("Informe a solução aplicada.")
        return Status.RESOLVED
```

[Ver código em `chamados/domain.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/domain.py#L57-L63).

**Benefício.** As regras e mensagens de cada estado ficam juntas. **Custo.** Uma pessoa que lê o fluxo passa pelo mapa de estados e pela classe concreta. O estado precisa ser convertido de/para um valor persistido.

[Diagrama de classes · State](../diagrams/classes-state.md) · [Refactoring Guru](https://refactoring.guru/pt-br/design-patterns/state)

## Adapter · Estrutural

**Problema.** A conexão SQLite expõe comandos SQL e retorna linhas. A aplicação precisa consultar e gravar objetos do domínio com um contrato independente do banco.

```python
def get(self, ticket_id: str) -> Ticket:
    row = self.connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    if row is None:
        raise TicketError("Chamado não encontrado.")
    return self._ticket_from_row(row)
```

[Ver código em `chamados/storage.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/storage.py#L77-L81).

**Benefício.** SQL, conversão de tipos e transações ficam confinados ao adaptador. **Custo.** O adaptador precisa acompanhar as alterações de esquema e as mudanças nos campos dos objetos.

[Diagrama de classes · Adapter](../diagrams/classes-adapter.md) · [Refactoring Guru](https://refactoring.guru/pt-br/design-patterns/adapter)
