from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from typing import ClassVar, Protocol


class TicketError(Exception):
    """Erro de negócio apresentado ao operador."""


class Severity(StrEnum):
    LOW = "baixa"
    MEDIUM = "media"
    HIGH = "alta"


class Action(StrEnum):
    START = "iniciar"
    RESOLVE = "resolver"
    REOPEN = "reabrir"


class Status(StrEnum):
    OPEN = "aberto"
    IN_PROGRESS = "em_atendimento"
    RESOLVED = "resolvido"


@dataclass(frozen=True)
class Ticket:
    id: str
    room: str
    title: str
    severity: Severity
    status: Status
    policy: str
    created_at: datetime
    due_at: datetime
    version: int = 0

    def advance(self, action: Action, note: str) -> "Ticket":
        next_status = STATES[self.status].transition(action, note.strip())
        return replace(self, status=next_status, version=self.version + 1)


class TicketState(Protocol):
    def transition(self, action: Action, note: str) -> Status: ...


class OpenState:
    def transition(self, action: Action, note: str) -> Status:
        if action is not Action.START:
            raise TicketError("Chamado aberto só pode iniciar atendimento.")
        return Status.IN_PROGRESS


class InProgressState:
    def transition(self, action: Action, note: str) -> Status:
        if action is not Action.RESOLVE:
            raise TicketError("Chamado em atendimento só pode ser resolvido.")
        if not note:
            raise TicketError("Informe a solução aplicada.")
        return Status.RESOLVED


class ResolvedState:
    def transition(self, action: Action, note: str) -> Status:
        if action is not Action.REOPEN:
            raise TicketError("Chamado resolvido só pode ser reaberto.")
        if not note:
            raise TicketError("Informe o motivo da reabertura.")
        return Status.OPEN


STATES: dict[Status, TicketState] = {
    Status.OPEN: OpenState(),
    Status.IN_PROGRESS: InProgressState(),
    Status.RESOLVED: ResolvedState(),
}


@dataclass(frozen=True)
class HistoryEntry:
    ticket_id: str
    status: Status
    at: datetime
    note: str


class DeadlinePolicy(Protocol):
    name: ClassVar[str]

    def deadline(self, severity: Severity, opened_at: datetime) -> datetime: ...
