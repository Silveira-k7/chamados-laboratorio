# 5. SOLID

## S · Responsabilidade única

`Ticket.advance` aplica a transição de domínio. A gravação e o histórico são responsabilidade do adaptador e do caso de uso. Isso permite mudar a exigência de nota sem editar SQL.

```python
def advance(self, action: Action, note: str) -> "Ticket":
    next_status = STATES[self.status].transition(action, note.strip())
    return replace(self, status=next_status, version=self.version + 1)
```

[Ver código em `chamados/domain.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/domain.py#L41-L43).

## O · Aberto/fechado

O serviço recebe a política de prazo pelo contrato. A lógica de abertura aceita outra implementação sem incluir condicionais por calendário dentro do caso de uso. A seleção ocorre na CLI.

```python
class DeadlinePolicy(Protocol):
    name: ClassVar[str]

    def deadline(self, severity: Severity, opened_at: datetime) -> datetime: ...
```

[Ver código em `chamados/domain.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/domain.py#L90-L93).

## L · Substituição de Liskov

As duas políticas aceitam toda gravidade declarada e devolvem prazo posterior ao instante de abertura. Um chamado pode ser criado com qualquer uma pelo mesmo serviço. O teste exercita ambas pela mesma operação.

```python
def test_queue_prioritizes_deadline(self):
    regular = self.service.open("Lab 4", "Falha no projetor", Severity.HIGH, RegularDeadline())
    self.assertEqual(self.ticket.due_at, self.now + timedelta(minutes=30))
    self.assertEqual(regular.due_at, self.now + timedelta(hours=4))
    self.assertEqual(triage_queue(self.storage), [self.ticket, regular])
```

[Ver código em `tests/test_chamados.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/tests/test_chamados.py#L21-L25).

## I · Segregação de interfaces

A fila depende só da leitura de pendências. O consumidor da fila pode usar uma fonte que implemente `pending` sem precisar expor gravações ou histórico.

```python
class QueueReader(Protocol):
    def pending(self) -> Sequence[Ticket]: ...
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L27-L28).

## D · Inversão de dependência

O serviço de chamados recebe portas de leitura e gravação e uma função de relógio. O ponto de entrada injeta SQLite e relógio UTC. Os testes injetam horário fixo para reproduzir os prazos.

```python
def __init__(self, reader: TicketReader, writer: TicketWriter, now: Callable[[], datetime]):
    self.reader = reader
    self.writer = writer
    self.now = now
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L55-L58).
